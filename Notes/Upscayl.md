# Upscayl

Upscayl upscales images to a higher resolution.

## Models and Differences

**TL:DR**: Use `upscayl-standard`, `high-fidelity`, or `ultramix-balanced`. If only one isn't good enough, manually create a composite.

Note: Custom models do exist, but I don't mention them here. These are just the default models in order.

### Upscayl Standard

`upscayl-standard` is a newer model, which can keep a lot of detail. Compared to `high-fidelity` it adds harder edges, does a bit of colour shifts, and a lot of detail is removed.

Sometimes good, but not consistent.

### High Fidelity

This models is quite similar to `upscayl-standard`, but tries to keep everything as close to source possible. By doing that, it sometimes fails by hallucinating detail that never existed.

Sometimes "shimmers" can be created. They're bad hallucinations, which are just annoying.

### Remacri (Non Commercial)

`remacri` blurs the output a lot. It should essentially never be used, as other models are much better.

### Ultramix Balanced

`ultramix-balanced` is quite interesting.

Unlike `upscayl-standard` or `high-fidelity` it removes noise, meaning the resulting image may look less detailed. However, It tends to have sharper edges than any of the two.

It effectively is `high-fidelity`, but with much less or no noise, but with sharper edges. This doesn't mean that all noise is removed, however it sometimes removes noise.

Surisingly effective and consistent, even though it's an older model.

### Ultrasharp (Non Commercial)

`ultrasharp` is effectively `ultramix-balanced`, but with much more pronounced edges, but not in a good way. It should only be used when necessary.

### Digital Art

`digital-art` removes a lot of detail and focuses on simple colours with not a lot of shading. It should only be used when necessary.

### realESRGAN General

Note: I don't know what the difference between the default and WDN is.

Incredibly fast model with little to no noise. Can be used as an alternative to Ultramix.

### 4xLSDIRplusC

Sometimes more effective than Ultramix.
