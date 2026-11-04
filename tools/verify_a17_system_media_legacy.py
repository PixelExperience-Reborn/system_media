#!/usr/bin/env python3
"""Historical Qualcomm audio-config source audit: not audio-policy runtime validation."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]

def require(cond, label):
    if not cond: raise AssertionError(label)
    print("PASS historical system/media:",label)

try:
    header=(ROOT/"audio/include/system/audio_config.h").read_text()
    audiobp=(ROOT/"audio/Android.bp").read_text()
    utilsbp=(ROOT/"audio_utils/Android.bp").read_text()
    routebp=(ROOT/"audio_route/Android.bp").read_text()
    camerabp=(ROOT/"camera/Android.bp").read_text()
    require("audio_get_configuration_paths()" in header, "audio config directory precedence function")
    require('property_get_bool("ro.vendor.qti.va_aosp.support", false)' in header,
            "old Qualcomm QSSI device-vendor branch present")
    require('property_get("ro.boot.product.vendor.sku"' in header,
            "old SKU-specific vendor lookup present")
    require('"_qssi"' in header and '"/vendor/etc/audio"' in header,
            "legacy QSSI and vendor audio search directories")
    require('"/odm/etc"' in header and '"/vendor/etc"' in header and '"/system/etc"' in header,
            "legacy fallback directory chain")
    require("audio_get_audio_policy_config_file()" in header,
            "audio policy Bluetooth offload variants are also affected")
    for name,body in (("libaudio_system_headers",audiobp),("libaudioutils",utilsbp),
                      ("libaudioroute",routebp),("libcamera_metadata",camerabp)):
        require(f'name: "{name}"' in body, "shared audio/camera native library "+name)
    require((ROOT/"TEST_MAPPING").is_file(), "old media test mapping retained")
    print("PASS archive source only. Device vendor property/files, audio HAL, Soong and real playback NOT TESTED.")
except (AssertionError,OSError) as exc:
    print("FAIL:",exc,file=sys.stderr)
    sys.exit(1)
