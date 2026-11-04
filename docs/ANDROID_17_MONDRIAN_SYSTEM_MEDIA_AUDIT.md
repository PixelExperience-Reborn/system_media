# P1 — system/media Android17 / mondrian Qualcomm audio config and ABI audit

Date: 2026-11-04. **Historical source inventory only; no Android17 platform override or device audio HAL build.**

## Provenance and real scope

- Archived PixelExperience-Reborn `system_media` branch `seventeen`, SHA `830312647a382e3d7e1ddbf4f5c14ccf7348b992`, merged Android14 r21 (2024-01-30).
- Official AOSP17 r1 `platform/system/media` exact Git tree `a70b18bcf8df9ea56f82c32fab883e5fff23a1ea`: https://android.googlesource.com/platform/system/media/+/refs/tags/android-17.0.0_r1/ . Contains `audio`, `audio_utils`, `audio_effects`, `audio_route`, `alsa_utils`, `camera`, `radio` and more, all of which must be kept consistent with framework and HALs.
- The staged PE-Reborn Android17 manifest selects **official `platform/system/media`**. The old PE archive is not an Android17 source.

## PE patch requiring device-specific review

`f5be7f966436d1dbb10a45c89f941b71bc8b5841` (2020), "media: update path for vendor specific config files", modifies `audio/include/system/audio_config.h`. The archived PE function `audio_get_configuration_paths()` reads `ro.vendor.qti.va_aosp.support` and `ro.boot.product.vendor.sku` and conditionally searches:
- `/odm/etc`
- `/vendor/etc/audio/sku_<sku>_qssi` (when Qualcomm property true)
- `/vendor/etc/audio/sku_<sku>`
- `/vendor/etc/audio` (when Qualcomm property true)
- `/vendor/etc`
- `/system/etc`

These paths are broad global audio-policy discovery behavior; the patch was written for QSSI/GSI differences, **not a demonstrated mondrian-specific need**. Setting this vendor property or changing search order without verifying **actual selected vendor blobs/config files and intended audio policy** can cause a wrong audio-policy XML to be loaded, break routing, voice calls, Bluetooth/offload or produce insecure fallback behavior.

Official AOSP17 `audio/include/system/audio_config.h` blob `6117f21442e8834e96fa3ff13ef492cdbf2a5c1a` performs `ro.boot.product.vendor.sku` based selection and uses `/odm/etc`, `/vendor/etc/audio/sku_<sku>`, `/vendor/etc`, `/system/etc`, **without** `ro.vendor.qti.va_aosp.support` or the `_qssi` path. It also selects `audio_policy_configuration.xml` variants for Bluetooth A2DP and LE Audio offload. Source: https://android.googlesource.com/platform/system/media/+/refs/tags/android-17.0.0_r1/audio/include/system/audio_config.h

## Why no broad old source replacement

- `audio/Android.bp` defines `libaudio_system_headers` and audio base types; `audio_utils/Android.bp` defines `libaudioutils`/fast math and other native libraries; `audio_route/Android.bp` defines `libaudioroute` and `libaudioroutev2`; `camera/Android.bp` exposes `libcamera_metadata`. Their APIs and ABI are shared across Android17 framework/media stack, AIDL/HIDL HALs, vendor modules and camera providers.
- Keeping old PE tree would override **all** audio/camera system native libraries merely to change one Qualcomm config path. This fails the project goal of a clean AOSP17 source base, and would introduce hard-to-track Soong/VINTF/ABI compatibility hazards.
- Before authoring independent PE-Reborn `device/xiaomi/mondrian` and `device/xiaomi/sm8450-common` product trees, inspect vendor extraction and the actual `audio_policy_configuration.xml`, mixer paths and HAL libraries in the device's partitions. Existing LF52406 LineageOS-based vendor/device trees are **hardware information only**, never the new PE build inheritance.
- If a needed vendor config genuinely resides in a non-standard location, prefer an **explicit device/vendor product file install path/overlay** after proving upstream AOSP17 discovery cannot resolve it. Any platform-wide patch must be narrowly scoped, backed by actual file paths, the property values used at boot and an on-device audio policy test.

## Required device and integration tests

1. Pin PE-Reborn vendor proprietary blob extraction, OEM/ODM audio policy path ownership and SELinux read access. Verify `ro.boot.product.vendor.sku` on real device and do not invent `ro.vendor.qti.va_aosp.support`.
2. Build official `system/media`, audio AIDL/HIDL interfaces, `libaudioutils`, `libaudio_system_headers`, `libcamera_metadata`, Media/Codec/AudioFlinger interactions in Android17 Soong.
3. Validate sound output/input, Bluetooth/A2DP and LE audio, USB/wired, DSP offload, voice recording, routing during phone calls, and Dolby effects only where their actual HAL and license permit. Check effects XML against installed libs.
4. Validate camera provider metadata, video recording audio/video sync, permissions, and CTS/VTS Audio/Camera suites.
5. Reboot/OTA regression, permission denials and performance with the actual new native PE-Reborn mondrian image.

## Status

- [x] Archived PE source revision and Qualcomm QSSI audio path patch reviewed.
- [x] Official Android17 exact source tree and generic audio config fallback identified.
- [x] Host-only archive/source CI authored.
- [ ] Exact official source-tag integrity CI confirmation.
- [ ] Android17 Soong/AIDL/HIDL audio-camera build and blob ABI checks.
- [ ] Real mondrian audio policy, HAL, CTS/VTS and recovery/OTA tests.

**Decision:** keep official AOSP17 `platform/system/media` and do not apply `ro.vendor.qti.va_aosp.support` path logic without proof from new PE vendor partition contents.
