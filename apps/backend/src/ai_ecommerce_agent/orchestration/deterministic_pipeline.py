"""The bounded synchronous Fast Lane pipeline.

This module owns one public application seam: a five-call deterministic
candidate generation pipeline.  It deliberately consumes the existing skill
output specs and the existing provider-neutral runtime/validator seams.  No
candidate becomes a confirmed Domain version here.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelCallResult,
    ModelExecutionProfile,
    ModelOutputEnvelope,
    ModelRuntimePort,
    ModelRuntimeVersionTuple,
    ProviderAttemptId,
    ProviderCallMetadata,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.application.structured_output import (
    parse_and_validate_structured_output,
)
from ai_ecommerce_agent.platform.model_runtime.scripted import (
    ScriptedModelRuntime,
    ScriptedModelScenario,
    ScriptedModelStep,
)
from ai_ecommerce_agent.shared_kernel.structured_content import StructuredContent

_ANCHOR: Final[str] = "anchor-city-commuter-backpack"
_REQUIRED_MARKERS: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    ("product identity", ("城市通勤双肩包", "CBP-SYN-001", _ANCHOR)),
    ("core use", ("通勤", "commuter")),
    ("product features", ("约 18 升", "18 升", "14 英寸", "laptop")),
    ("source evidence", ("product.json", "direct_source", "source-sufficient")),
)


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Validated candidates or an honest deterministic preflight limitation."""

    status: str
    missing_information: tuple[str, ...]
    candidates: tuple[tuple[str, StructuredContent], ...]


RuntimeFactory = Callable[
    [tuple[ModelCallRequest, ...], tuple[str, ...]], ModelRuntimePort
]
SpecFactory = Callable[[], StructuredOutputSpec]


def _json(value: Mapping[str, object]) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _candidate_payloads(input_text: str) -> tuple[Mapping[str, object], ...]:
    """Return the fixed Anchor SKU candidate payloads.

    Every product claim below is copied from the accepted synthetic Anchor SKU
    fixture.  Audience and positioning statements are explicitly hypotheses,
    and unsupported market or efficacy claims are not emitted.
    """

    intake: Mapping[str, object] = {
        "intake_assessment": {
            "completeness_level": "evidence_rich",
            "runnable": True,
            "available_source_types": [
                extension
                for extension, marker in (
                    ("json", ".json"),
                    ("markdown", ".md"),
                    ("txt", ".txt"),
                    ("csv", ".csv"),
                )
                if marker in input_text.casefold()
            ],
            "excluded_sources": ["real customer research", "competitor results"],
            "missing_information": ["真实销量、转化、竞品或用户研究数据"],
            "warnings": ["防泼水描述不支持绝对防水或耐久性结论"],
        },
        "fact_candidates": [
            {
                "category": "product_identity",
                "attribute_key": "display_name",
                "raw_value": "城市通勤双肩包",
                "normalized_value": "城市通勤双肩包",
                "unit": None,
                "assertion_type": "direct_fact",
                "supporting_fragment_ids": ["product.json#product_identity"],
                "contradicting_fragment_ids": [],
                "notes": [],
            },
            {
                "category": "capacity",
                "attribute_key": "capacity",
                "raw_value": "约 18 升",
                "normalized_value": "约 18 升",
                "unit": "升",
                "assertion_type": "direct_fact",
                "supporting_fragment_ids": ["product.json#attributes[0]"],
                "contradicting_fragment_ids": [],
                "notes": [],
            },
            {
                "category": "laptop_fit",
                "attribute_key": "laptop_fit",
                "raw_value": "可放入 14 英寸级别笔记本电脑",
                "normalized_value": "可放入 14 英寸级别笔记本电脑",
                "unit": None,
                "assertion_type": "direct_fact",
                "supporting_fragment_ids": ["product.json#attributes[1]"],
                "contradicting_fragment_ids": [],
                "notes": ["购买前仍需确认设备尺寸"],
            },
            {
                "category": "weather_cover",
                "attribute_key": "weather_cover",
                "raw_value": "表面有防泼水处理，不能替代长期浸水防护",
                "normalized_value": "表面有防泼水处理，不能替代长期浸水防护",
                "unit": None,
                "assertion_type": "documented_claim",
                "supporting_fragment_ids": ["product.json#attributes[2]"],
                "contradicting_fragment_ids": [],
                "notes": ["不得升级为绝对防水"],
            },
        ],
        "claims_requiring_verification": [],
        "conflicts_and_limitations": {
            "source_conflicts": [],
            "evidence_limitations": [
                "未提供真实销量、转化、竞品或用户研究数据",
                "防泼水描述不支持绝对防水或耐久性结论",
            ],
            "insufficient_information": ["真实用户研究与相对竞品证据"],
            "hypotheses_to_validate": [],
        },
        "workflow_stage_decision": "valid",
    }
    insight: Mapping[str, object] = {
        "evidence_assessment": {
            "mode": "evidence_backed",
            "evidence_coverage": "anecdotal",
            "source_types": ["product_facts"],
            "source_set_version_id": "fixture-sufficient-v1",
            "sample_summary": (
                "Supplied product evidence only; not a population estimate."
            ),
            "limitations": ["没有真实用户研究或规模数据"],
        },
        "themes": [
            {
                "label": "通勤收纳与取用",
                "evidence_coverage": "anecdotal",
                "source_scopes": ["fixture-sufficient-v1"],
                "supporting_fragment_ids": ["product.json#attributes[1]"],
                "contradicting_fragment_ids": [],
                "limitations": ["合成资料不代表总体用户"],
            }
        ],
        "customer_insights": [
            {
                "insight_type": "documented_signal",
                "statement": "工作日城市通勤需要携带电脑、文件和日常随身物品",
                "audience_segment": "工作日城市通勤者",
                "usage_context": "工作日城市通勤",
                "user_problem_or_need": "需要在通勤中携带电脑、文件和日常随身物品",
                "underlying_reason": "商品资料记录了工作日通勤用途和电脑收纳事实",
                "behavioral_or_purchase_impact": "可作为内容沟通方向",
                "evidence_coverage": "anecdotal",
                "source_scopes": ["fixture-sufficient-v1"],
                "supporting_fragment_ids": [
                    "product.json#product_identity",
                    "product.json#attributes[1]",
                ],
                "contradicting_fragment_ids": [],
                "dataset_statistic_ids": [],
                "customer_language_fragment_ids": [],
                "based_on_fact_ids": ["fact-laptop-fit"],
                "limitations": ["不是规模化用户研究结论"],
                "notes": [],
            }
        ],
        "hypotheses_to_validate": [
            {
                "statement": "清晰的通勤收纳方向可能适合需要携带电脑和文件的人群",
                "audience_segment": "工作日城市通勤者",
                "usage_context": "工作日城市通勤",
                "user_problem_or_need": "希望在通勤中有序携带电脑和文件",
                "underlying_reason": "资料记录了工作日通勤用途和电脑收纳事实",
                "behavioral_or_purchase_impact": "需要后续用户反馈验证",
                "source_scopes": ["fixture-sufficient-v1"],
                "supporting_fragment_ids": [],
                "contradicting_fragment_ids": [],
                "based_on_fact_ids": ["fact-product-identity"],
                "validation_needed": ["真实用户访谈或评论资料"],
                "limitations": ["合成资料不支持普遍化结论"],
                "notes": [],
            }
        ],
        "workflow_stage_decision": "valid_with_limitations",
    }
    positioning: Mapping[str, object] = {
        "positioning_context": {
            "facts_version_id": "fixture-sufficient-v1",
            "insights_version_id": "fixture-sufficient-v1",
            "competitor_source_set_version_id": None,
            "business_constraints": ["不做绝对防水或功效承诺"],
            "input_limitations": ["没有竞品资料和市场规模数据"],
        },
        "positioning_candidates": [
            {
                "candidate_id": "positioning-commuter-access",
                "candidate_title": "城市通勤的清晰收纳方案",
                "strategy_type": "functional_commuter",
                "target_segment": "工作日城市通勤者",
                "target_segment_is_hypothesis": True,
                "usage_context": "工作日携带电脑、文件和日常物品",
                "job_or_core_need": "在通勤移动中保持物品有序并便于取用",
                "job_or_core_need_is_hypothesis": False,
                "category_frame": "城市通勤双肩包",
                "value_proposition": "用约 18 升容量和电脑收纳支持日常通勤携带",
                "key_benefits": ["电脑取用更清晰", "日常物品集中收纳"],
                "differentiation": "以收纳路径作为机会方向，未完成竞品验证",
                "differentiation_is_opportunity_hypothesis": True,
                "reasons_to_believe": [
                    {
                        "statement": "资料提供了约 18 升容量和 14 英寸级别电脑收纳事实",
                        "based_on_fact_ids": ["fact-capacity", "fact-laptop-fit"],
                        "based_on_insight_ids": ["insight-commuter-access"],
                    }
                ],
                "proof_points": [
                    {
                        "statement": "可放入 14 英寸级别笔记本电脑",
                        "based_on_fact_ids": ["fact-laptop-fit"],
                    }
                ],
                "based_on_fact_ids": ["fact-capacity", "fact-laptop-fit"],
                "based_on_insight_ids": ["insight-commuter-access"],
                "competitor_evidence_ids": [],
                "assumptions": ["目标人群和差异化方向仍需验证"],
                "evidence_limitations": ["没有竞品资料或用户规模数据"],
                "strategic_risks": ["不得将防泼水描述写成绝对防水"],
                "evidence_profile": "documented_facts_plus_bounded_hypothesis",
                "ranking_rationale": "直接收纳事实最明确，适合作为首个候选方向",
            }
        ],
        "comparison_matrix": [
            {
                "candidate_id": "positioning-commuter-access",
                "target_segment": "工作日城市通勤者",
                "core_need": "有序携带和快速取用",
                "primary_value": "收纳路径清晰",
                "key_differentiation": "收纳体验机会假设",
                "evidence_profile": "documented_facts_plus_bounded_hypothesis",
                "main_risk": "缺少竞品验证",
            }
        ],
        "recommendation": {
            "recommended_candidate_id": "positioning-commuter-access",
            "recommendation_rationale": "该候选直接使用资料中的收纳事实",
            "conditions_for_success": ["确认电脑尺寸适配和用户需求"],
            "validation_needed": ["补充真实用户或竞品资料"],
        },
        "workflow_stage_decision": "ready_for_review_with_limitations",
    }
    marketing: Mapping[str, object] = {
        "brief_candidate": {
            "objective_and_audience": {
                "communication_objective": {
                    "primary_objective": "说明城市通勤中的清晰收纳价值",
                    "secondary_objectives": ["展示电脑收纳和日常物品携带"],
                    "business_assumption": True,
                },
                "audience": "工作日城市通勤者",
                "audience_context": ["携带电脑、文件和日常物品"],
                "audience_is_hypothesis": True,
            },
            "message_architecture": {
                "core_message": "为工作日通勤提供清晰的电脑与日常物品收纳",
                "message_hierarchy": {
                    "primary_message": "电脑收纳事实支持通勤携带",
                    "secondary_benefits": ["约 18 升容量", "日常物品有序放置"],
                    "supporting_proof_points": ["可放入 14 英寸级别笔记本电脑"],
                },
                "benefit_hierarchy": {
                    "primary_benefit": "减少通勤取用时的寻找成本",
                    "secondary_benefits": ["携带电脑和文件更清晰"],
                    "supporting_features": ["14 英寸级别电脑收纳", "约 18 升容量"],
                },
            },
            "reasons_to_believe_and_evidence": {
                "reasons_to_believe": [
                    {
                        "statement": "商品资料描述了 14 英寸级别电脑收纳",
                        "based_on_fact_ids": ["fact-laptop-fit"],
                        "based_on_insight_ids": ["insight-commuter-access"],
                    }
                ],
                "proof_points": [
                    {
                        "proof_point": "可放入 14 英寸级别笔记本电脑",
                        "fact_id": "fact-laptop-fit",
                        "supporting_fragment_ids": ["product.json#attributes[1]"],
                        "source_version_id": "source-sufficient-product-v1",
                        "approved_wording": (
                            "可放入 14 英寸级别笔记本电脑，购买前请确认设备尺寸"
                        ),
                    }
                ],
            },
            "execution_direction": {
                "objections": ["电脑尺寸是否适配"],
                "objection_responses": [
                    {
                        "objection": "电脑尺寸是否适配",
                        "response": (
                            "资料标注可放入 14 英寸级别设备，购买前仍需确认尺寸"
                        ),
                        "based_on_fact_ids": ["fact-laptop-fit"],
                        "based_on_insight_ids": [],
                        "insufficient_evidence": False,
                    }
                ],
                "content_angles": [
                    {
                        "angle_title": "通勤收纳路径",
                        "angle_type": "functional_demo",
                        "user_tension": "电脑和文件在通勤中需要快速取用",
                        "message_focus": "14 英寸级别电脑收纳与约 18 升容量",
                        "supporting_benefits": ["有序放置"],
                        "proof_points": ["可放入 14 英寸级别笔记本电脑"],
                        "hypothesis_status": "目标人群为待验证假设",
                        "requires_validation": True,
                        "risk_notes": ["不宣称普遍适合所有通勤者"],
                    }
                ],
                "tone_and_voice": {
                    "tone": "practical",
                    "voice": "clear and bounded",
                    "suggested_tone": True,
                },
                "call_to_action_objective": "引导用户检查设备尺寸和收纳需求",
            },
            "constraints_and_honesty": {
                "mandatory_messages": ["购买前确认设备尺寸"],
                "prohibited_claims": ["绝对防水", "保证舒适", "提高转化"],
                "accepted_hypotheses": ["目标人群为工作日城市通勤者"],
                "hypotheses_to_test": ["收纳路径是否改善通勤体验"],
                "evidence_limitations": ["没有真实用户研究、销量或竞品资料"],
                "risk_notes": ["防泼水只按资料原文表达"],
                "platform_adaptation_rules": ["后续由小红书 Adapter 映射"],
            },
        },
        "version_and_workflow_context": {
            "approved_strategy_version_id": "candidate-positioning-commuter-access",
            "facts_version_id": "fixture-sufficient-v1",
            "insights_version_id": "fixture-sufficient-v1",
            "input_limitations": ["没有竞品资料或真实用户研究"],
            "stage_decision": "valid_with_limitations",
        },
    }
    xiaohongshu: Mapping[str, object] = {
        "xiaohongshu_brief_candidate": {
            "platform_and_campaign_context": {
                "platform": "小红书",
                "account_type": None,
                "content_relationship": "从通用 Marketing Brief 映射",
                "commercial_context": "城市通勤双肩包内容策划",
                "campaign_objective": "展示清晰收纳价值",
                "available_asset_types": ["product_detail", "usage_demo"],
            },
            "note_format_and_content_mode": {
                "recommended_note_format": "image_text_note_brief",
                "primary_content_mode": "通勤收纳场景",
                "secondary_content_mode": "电脑取用演示",
                "platform_objective": "帮助读者理解收纳路径",
                "source_content_angle_ids": ["angle-commuter-storage"],
            },
            "creative_structure_directions": {
                "title_directions": [
                    {
                        "title_direction": "通勤包如何把电脑和日常物品放得更清楚",
                        "user_question_or_tension": "通勤时电脑和文件如何快速取用",
                        "primary_keyword": "通勤收纳",
                        "message_focus": "14 英寸级别电脑收纳",
                        "proof_required": True,
                        "risk_notes": ["不写绝对化效果"],
                    }
                ],
                "cover_direction": {
                    "cover_message_direction": "展示电脑收纳和日常物品携带",
                    "cover_visual_focus": "通勤物品分区",
                    "cover_information_priority": "先展示真实收纳事实",
                    "cover_risk_notes": ["不制造未提供的物品或场景"],
                },
                "narrative_structure": [
                    {
                        "module_name": "问题",
                        "content_direction": "通勤中寻找电脑和文件",
                        "proof_points": ["14 英寸级别电脑收纳"],
                        "limitations": ["仅为合成资料"],
                        "risk_notes": [],
                    },
                    {
                        "module_name": "解决方式",
                        "content_direction": "按收纳分区演示取用",
                        "proof_points": ["可放入 14 英寸级别笔记本电脑"],
                        "limitations": ["购买前需确认设备尺寸"],
                        "risk_notes": [],
                    },
                ],
                "content_angle_mappings": [
                    {
                        "source_content_angle_id": "angle-commuter-storage",
                        "xiaohongshu_angle": "城市通勤收纳路径",
                        "note_format": "image_text_note_brief",
                        "content_mode": "usage_demo",
                        "narrative_structure": ["问题", "解决方式"],
                        "proof_points": ["14 英寸级别电脑收纳", "约 18 升容量"],
                        "customer_language": [],
                        "hypotheses": ["目标读者为工作日城市通勤者"],
                        "limitations": ["缺少真实研究与竞品对比"],
                        "risk_notes": ["不宣称绝对防水"],
                    }
                ],
                "message_priority": ["清晰收纳", "电脑取用", "设备尺寸提示"],
                "proof_placement": [
                    {
                        "proof_point": "可放入 14 英寸级别笔记本电脑",
                        "narrative_module": "解决方式",
                        "placement_direction": "在收纳演示中标注来源事实",
                    }
                ],
                "fit_boundary": "仅映射通用 Brief，不生成最终发布内容",
            },
            "discovery_and_action_directions": {
                "search_intent": "寻找通勤电脑收纳方案",
                "keyword_directions": ["通勤收纳", "电脑收纳"],
                "topic_directions": ["工作日通勤"],
                "hashtag_directions": ["通勤包", "城市通勤"],
                "cta_mapping": {
                    "source_cta_objective": "检查设备尺寸和收纳需求",
                    "cta_direction": "引导读者核对设备尺寸",
                    "risk_notes": [],
                },
                "interaction_prompt_direction": "询问读者通勤时最常取用的物品",
            },
            "evidence_and_platform_constraints": {
                "proof_points": ["14 英寸级别电脑收纳", "约 18 升容量"],
                "customer_language": [],
                "mandatory_messages": ["购买前确认设备尺寸"],
                "prohibited_claims": ["绝对防水", "保证舒适", "提高转化"],
                "hypotheses": ["目标读者为工作日城市通勤者"],
                "evidence_limitations": ["合成资料，不代表真实用户研究"],
                "platform_risk_notes": ["遵守事实和证据边界"],
                "review_route_notes": ["结果仍需人工 Review"],
                "required_qualification_notes": ["防泼水按资料原文限定"],
                "commercial_disclosure_notes": [],
            },
        },
        "workflow_and_version_context": {
            "marketing_brief_version_id": "candidate-marketing-brief",
            "approved_strategy_version_id": "candidate-positioning-commuter-access",
            "facts_version_id": "fixture-sufficient-v1",
            "platform_policy_snapshot_id": None,
            "platform_policy_version": None,
            "input_limitations": ["没有竞品资料或真实用户研究"],
            "stage_decision": "valid_with_limitations",
        },
    }
    return (intake, insight, positioning, marketing, xiaohongshu)


def _specs(
    spec_factories: Sequence[SpecFactory],
) -> tuple[StructuredOutputSpec, ...]:
    if len(spec_factories) != 5:
        raise ValueError("exactly five ordered output spec factories are required")
    return tuple(factory() for factory in spec_factories)


def _request(
    input_text: str,
    spec: StructuredOutputSpec,
    index: int,
    upstream: StructuredContent | None,
) -> ModelCallRequest:
    call_id = ModelCallId(f"deterministic-stage-{index}")
    profile = ModelExecutionProfile("mvp0-fast-lane-deterministic", "v1")
    return ModelCallRequest(
        identity=ModelCallIdentity(call_id),
        instructions=f"Produce the validated {spec.output_schema_id} candidate.",
        context=StructuredContent.from_mapping(
            {
                "primary_input": input_text,
                "upstream_candidate": (
                    upstream.to_mapping() if upstream is not None else None
                ),
            }
        ),
        structured_output=spec,
        execution_profile=profile,
        contract_versions=ModelCallContractVersions(
            prompt_template_id=f"mvp0-stage-{index}",
            prompt_template_version="v1",
            skill_contract_version="v1",
            domain_validator_version="v1",
            context_assembly_version="v1",
        ),
    )


def build_scripted_runtime(
    requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
) -> ModelRuntimePort:
    """Build the deterministic substitute for one coordinator invocation."""

    steps: list[ScriptedModelStep] = []
    for request, payload in zip(requests, payloads, strict=True):
        call_id = request.identity.model_call_id
        version_tuple = ModelRuntimeVersionTuple(
            provider_id="scripted",
            api_family="deterministic",
            sdk_version="n/a",
            configured_model_id="mvp0-scripted",
            resolved_model_id="mvp0-scripted",
            prompt_template_id=request.contract_versions.prompt_template_id,
            prompt_template_version=request.contract_versions.prompt_template_version,
            output_schema_id=request.structured_output.output_schema_id,
            output_schema_version=request.structured_output.output_schema_version,
            skill_contract_version=request.contract_versions.skill_contract_version,
            domain_validator_version=request.contract_versions.domain_validator_version,
            execution_profile_id=request.execution_profile.execution_profile_id,
            execution_profile_version=request.execution_profile.execution_profile_version,
            context_assembly_version=request.contract_versions.context_assembly_version,
        )
        result = ModelCallResult(
            output_envelope=ModelOutputEnvelope(payload),
            provider_metadata=ProviderCallMetadata(
                model_call_id=call_id,
                provider_attempt_ids=(ProviderAttemptId(f"attempt-{call_id.value}"),),
                version_tuple=version_tuple,
                provider_response_id=None,
                provider_request_id=None,
                usage=None,
                latency_ms=0,
            ),
        )
        steps.append(
            ScriptedModelStep(
                expected_identity=request.identity,
                expected_execution_profile=request.execution_profile,
                expected_output_schema_id=request.structured_output.output_schema_id,
                expected_output_schema_version=request.structured_output.output_schema_version,
                outcome=result,
            )
        )
    return ScriptedModelRuntime(
        scenario=ScriptedModelScenario(
            scenario_id="mvp0-fast-lane-anchor-sku",
            steps=tuple(steps),
        )
    )


def _preflight(input_text: str) -> tuple[str, ...]:
    missing: list[str] = []
    for label, alternatives in _REQUIRED_MARKERS:
        if not any(
            marker.casefold() in input_text.casefold() for marker in alternatives
        ):
            missing.append(label)
    return tuple(missing)


class DeterministicPipelineCoordinator:
    """Run the fixed five-stage pipeline behind one small application seam."""

    def __init__(
        self,
        spec_factories: Sequence[SpecFactory],
        runtime_factory: RuntimeFactory = build_scripted_runtime,
    ):
        if len(spec_factories) != 5:
            raise ValueError("exactly five ordered output spec factories are required")
        self._spec_factories = tuple(spec_factories)
        self._runtime_factory = runtime_factory

    def generate(self, *, input_text: str) -> PipelineResult:
        if type(input_text) is not str:
            raise TypeError("input_text must be a string")
        if not input_text.strip():
            raise ValueError("input_text must be nonblank")
        missing = _preflight(input_text)
        if missing:
            return PipelineResult(
                status="insufficient_input",
                missing_information=tuple(
                    f"Provide Anchor SKU {label} evidence." for label in missing
                ),
                candidates=(),
            )

        payloads = tuple(_json(value) for value in _candidate_payloads(input_text))
        specs = _specs(self._spec_factories)
        # The scripted runtime only needs the stable call/spec metadata at
        # construction.  Actual requests are assembled below, one stage at a
        # time, after the previous stage has been parsed and validated.
        runtime_requests = tuple(
            _request(input_text, spec, index, None)
            for index, spec in enumerate(specs, start=1)
        )
        runtime = self._runtime_factory(runtime_requests, payloads)
        validated: list[tuple[str, StructuredContent]] = []
        upstream: StructuredContent | None = None
        for index, (spec, payload_name) in enumerate(
            zip(
                specs,
                (
                    "productIntake",
                    "customerInsight",
                    "productPositioning",
                    "marketingBrief",
                    "xiaohongshuBrief",
                ),
                strict=True,
            ),
            start=1,
        ):
            request = _request(input_text, spec, index, upstream)
            result = runtime.execute(request)
            candidate = parse_and_validate_structured_output(
                result=result,
                spec=request.structured_output,
            )
            validated.append((payload_name, candidate))
            upstream = candidate
        return PipelineResult(
            status="awaiting_review",
            missing_information=(),
            candidates=tuple(validated),
        )


__all__ = [
    "DeterministicPipelineCoordinator",
    "SpecFactory",
    "PipelineResult",
    "RuntimeFactory",
    "build_scripted_runtime",
]
