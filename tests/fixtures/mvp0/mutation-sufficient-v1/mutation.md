# mutation-sufficient-v1｜虚构变更脚本

> 这是 `fixture-sufficient-v1` 的 fictional / synthetic mutation instruction，不是已
> 执行的业务 Run，也不表示任何实现状态。

- **mutation_id:** `mutation-sufficient-v1`
- **base_fixture_id:** `fixture-sufficient-v1`
- **base_source_version:** `source-sufficient-product-v1`
- **replacement_source_version:** `source-sufficient-product-v2`
- **anchor_sku:** `anchor-city-commuter-backpack`
- **change_kind:** `business_semantic_fact_change`
- **change_locator:** `changed-product.json#attributes[0]`

## 变更

把商品容量资料从“约 18 升”更正为“约 20 升”。这是一个会影响事实层
和下游判断的业务语义修改，不是错别字、标点或展示性润色。

## 预期行为（供确定性测试和人工验收使用）

1. 新 Source Version 必须与旧版本可区分，旧版本保留为历史上下文。
2. 系统先展示失效 / 保留阶段和建议局部重跑起点；不能静默把旧下游
   结果继续当作 Current Truth。
3. 受影响的洞察、定位 / 策略、Review 输入和执行 Brief 应失效或被
   标记为 superseded；陈旧 Review 的保存 / 提交应被拒绝。
4. 只有用户确认影响预览后，才允许从最早受影响阶段局部重跑。重跑后
   受影响内容重新进入同一 Human Review 语义门禁。
5. 导出预览和最终 Markdown Snapshot 只能引用确认后的当前版本，不能
   把旧或失效结果伪装成当前结果。

本脚本描述行为门禁和人工判断输入，不锁定完整模型措辞，不把生成成功
或质量检查成功写成 approved。
