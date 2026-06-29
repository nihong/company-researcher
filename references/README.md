# References（知识库）

本目录用于存放投研所需的静态参考资料。按需扩展。

## 建议目录结构

```
references/
├── valuation/          # 估值方法论
│   ├── PE.md           # 市盈率估值法
│   ├── DCF.md          # 现金流贴现法
│   └── SOTP.md         # 分部估值法
│
├── industry/           # 行业专项模板
│   ├── medical.md      # 医药行业分析框架
│   ├── semiconductor.md # 半导体行业分析框架
│   ├── consumer.md     # 消费行业分析框架
│   ├── bank.md         # 银行行业分析框架
│   ├── EV.md           # 新能源汽车分析框架
│   └── AI.md           # AI/科技行业分析框架
│
├── frameworks/         # 通用分析框架
│   ├── porter.md       # 波特五力
│   ├── swot.md         # SWOT分析
│   └── moat.md         # 护城河分析
│
└── cache/              # 研究缓存（自动生成）
    └── .gitkeep
```

## 使用方式

- AI 在执行投研任务时，会根据需要自动读取本目录下的参考资料。
- 你可以随时往里面添加新的分析框架、行业模板、估值模型。
- `cache/` 目录用于存放通过 `opencli` 或 `search_web` 抓取的临时数据，自动管理。
