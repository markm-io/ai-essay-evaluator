# Changelog

## v1.3.3 (2025-12-01)

### Bug fixes

- Update dependency pandas-stubs to v2.3.3.251201 ([`548b5eb`](https://github.com/markm-io/ai-essay-evaluator/commit/548b5ebdfa99017aa751973716c842af31b1e235))

## v1.3.2 (2025-10-15)

## v1.3.1 (2025-10-15)

### Bug fixes

- Update renovate configuration to use recommended settings ([`8c41d6d`](https://github.com/markm-io/ai-essay-evaluator/commit/8c41d6d73acf11f66f89da3c49c62292236dba51))
- Use gh_pat to avoid oidc workflow validation errors ([`3cf5207`](https://github.com/markm-io/ai-essay-evaluator/commit/3cf5207601243961c9668e9db3cd3bb1e5ec51f4))

## v1.3.0 (2025-10-15)

### Features

- Update renovate configuration for automerging and package rules ([`8c3c675`](https://github.com/markm-io/ai-essay-evaluator/commit/8c3c675f64d8b2d866674496f158ad266bcb1f55))

## v1.2.0 (2025-10-15)

### Features

- Enhance cost analysis with model-specific pricing and add tests ([`ba7223a`](https://github.com/markm-io/ai-essay-evaluator/commit/ba7223a23a7d0892d849c19d375ca389a68af991))

### Bug fixes

- Refine grading instructions for evidence-based writing assessment ([`4ad2544`](https://github.com/markm-io/ai-essay-evaluator/commit/4ad254469f447ca0c52b112ed91b724656b822b6))

## v1.1.0 (2025-09-30)

### Features

- Enhance evaluation guidelines for evidence-based writing and plagiarism detection ([`ccc29ba`](https://github.com/markm-io/ai-essay-evaluator/commit/ccc29ba366fbf29318a3f74779e11530ec6578e9))
- Enhance documentation and installation instructions for ai essay evaluator ([`c84a42f`](https://github.com/markm-io/ai-essay-evaluator/commit/c84a42fb5bc4d43341c933753f652bca12442db2))

### Bug fixes

- Adjust cost calculations for uncached, cached, and output tokens ([`1ee608e`](https://github.com/markm-io/ai-essay-evaluator/commit/1ee608ea01f5a766df2e949a0ab4cfb9c3a2f447))

## v1.0.0 (2025-06-13)

## v0.9.0 (2025-04-08)

### Features

- Add language-specific feedback for blank student responses in openai client ([`1ed4377`](https://github.com/markm-io/ai-essay-evaluator/commit/1ed437771d76cc3f84d37ad8014f322edc658b13))

## v0.8.0 (2025-04-08)

### Features

- Enhance openai client with improved response handling and validation checks ([`0bfb3e0`](https://github.com/markm-io/ai-essay-evaluator/commit/0bfb3e0dc3b01c4a32794fd4c677def3899153cf))

## v0.7.0 (2025-03-26)

### Features

- Enhance openai client with adaptive rate limiting and improved error handling ([`aadaad3`](https://github.com/markm-io/ai-essay-evaluator/commit/aadaad398913564634bd15ff32a621b7a9a5b535))
- Enhance cost analysis by improving token calculation and adding detailed tests ([`753b9ea`](https://github.com/markm-io/ai-essay-evaluator/commit/753b9ea4f09cc5820719704cae104632601c2bd7))

## v0.6.0 (2025-03-25)

## v0.5.0 (2025-03-25)

### Features

- Implement asynchronous logging with asynclogger and integrate into csv processing ([`c84b7af`](https://github.com/markm-io/ai-essay-evaluator/commit/c84b7af81e2aa2cbbdbde263d3bba91724bbdeb9))
- Refactor text normalization and enhance csv handling with column reordering for total_score ([`40dc9fc`](https://github.com/markm-io/ai-essay-evaluator/commit/40dc9fcbf46055e4ff4a029b5f6c46dd784a72be))
- Enhance logging setup to ensure proper file handler closure on exit ([`eb8d049`](https://github.com/markm-io/ai-essay-evaluator/commit/eb8d049201d119703d6a43137615bd3e4046d04e))
- Add option to calculate scoring totals and enhance csv handling with text normalization ([`e05fd32`](https://github.com/markm-io/ai-essay-evaluator/commit/e05fd32b14f8c9cd6d2a6b94f3e3770af8cd4ae7))
- Enhance error logging and process rows in batches for improved performance ([`7a059d3`](https://github.com/markm-io/ai-essay-evaluator/commit/7a059d3338b783b5175e45c409b12603877dd01f))
- Implement semaphore for concurrent processing in openai client ([`63e9d5f`](https://github.com/markm-io/ai-essay-evaluator/commit/63e9d5f8abbfd39009053495ade3bd61cdc731c6))
- Add progress display and logging enhancements in essay evaluation process ([`db372e6`](https://github.com/markm-io/ai-essay-evaluator/commit/db372e6e5606ba90c833547bb2e231d42230fde9))

### Bug fixes

- Add character replacement for problematic sequences in text normalization ([`f7978dc`](https://github.com/markm-io/ai-essay-evaluator/commit/f7978dcd2153bac4148303208dabac3baac0d855))
- Update merge columns in file handler to use correct identifiers ([`c7db5be`](https://github.com/markm-io/ai-essay-evaluator/commit/c7db5be7228045ed913c0a97f395056f8a2a4202))
- Enhance csv merging functionality to preserve scoring format and pass information ([`ab3bb90`](https://github.com/markm-io/ai-essay-evaluator/commit/ab3bb9013027a5cb2720ca68a1bcf9ffff61cc0c))
- Update token cost display to include both cached and uncached tokens ([`079334b`](https://github.com/markm-io/ai-essay-evaluator/commit/079334bcb46f21990665b405e294920ccaf893ad))

## v0.4.0 (2025-03-21)

### Features

- Add feedback for verbatim responses in ai grading evaluation ([`ae8a816`](https://github.com/markm-io/ai-essay-evaluator/commit/ae8a816e8747a7deba00c6a075d6f4a0550d63e7))

## v0.3.0 (2025-03-05)

### Features

- Add rate limiting handling and reset time parsing in openai client ([`bc03369`](https://github.com/markm-io/ai-essay-evaluator/commit/bc03369ec2367f5b07b68d26dd5ce80fa0c8aafa))
- Enhance cost analysis by accumulating usage details and updating cost calculation logic ([`54141c6`](https://github.com/markm-io/ai-essay-evaluator/commit/54141c6826a368e91ec7b9b38224f807abac413d))
- Refactor openai client integration to use asyncopenai and improve error handling ([`bda29f7`](https://github.com/markm-io/ai-essay-evaluator/commit/bda29f727f0e9f602afcb78eb137bb758dbb536d))
- Rename grader to evaluator in cli and update command options ([`e2031ea`](https://github.com/markm-io/ai-essay-evaluator/commit/e2031ea9d2acb1f8fa11f0ddf1fa296f1ae2e0a2))

## v0.2.0 (2025-03-05)

### Features

- Add pre-push hook to check for remote updates ([`d2914eb`](https://github.com/markm-io/ai-essay-evaluator/commit/d2914eba7d64bf9b74aea4a17bd890cabb9081ac))

## v0.1.1 (2025-03-05)

## v0.1.0 (2025-03-05)

### Bug fixes

- Update numpy version constraints and remove redundant entries in uv.lock ([`f654511`](https://github.com/markm-io/ai-essay-evaluator/commit/f654511d4e9fe21ff5d782828a1dce9882b494ae))

### Features

- Rename cli commands for clarity and consistency ([`5e0d7da`](https://github.com/markm-io/ai-essay-evaluator/commit/5e0d7da7db17b0776d3e1d3bc310ccb1a5518553))
- Implement cli for grading and fine-tuning jsonl files ([`9754cf0`](https://github.com/markm-io/ai-essay-evaluator/commit/9754cf025df3fe756860216366122d75b4aebb99))
- Implement cli for grading and fine-tuning jsonl files ([`6bc9be9`](https://github.com/markm-io/ai-essay-evaluator/commit/6bc9be9cc268a956319b9065d3f3be3f54d896f2))

### Documentation

- Add @markm-io as a contributor ([`ff91236`](https://github.com/markm-io/ai-essay-evaluator/commit/ff912366d1c155713aaf4513bb93bd400593d525))
