# 身份冲突｜虚构恢复场景

> 本文件是 `fixture-conflict-v1` 的 fictional / synthetic 测试资料。
> 两个值都由测试资料提供，不代表真实 SKU、仓库或商家系统。

- **anchor_sku:** `anchor-city-commuter-backpack`
- **conflict_type:** `blocking_product_identity`
- **locator:** `identity-conflict.md#conflict`

## 冲突

在 `source-conflict-catalog` / `source-conflict-catalog-v1` 中，商品身份
标识为 **CBP-SYN-001**；在 `source-conflict-warehouse-note` /
`source-conflict-warehouse-v1` 中，同一虚构商品上下文被标为 **CBP-SYN-009**。

该差异会影响事实层的商品身份和下游证据归属。模型或确定性替身不得凭
常识裁决，也不得把任一值写成最终 Current Truth。

## 允许的行动

用户可选择确认一个值、补充一份新的版本化来源，或取消本次处理。完成
动作后，只从冲突解决后的事实阶段恢复；未确认前不得生成最终 Brief。
