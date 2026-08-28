# Changelog

## 0.1.0 (2026-08-28)


### ⚠ BREAKING CHANGES

* **mqtt:** devices must set WATER_LOW_CM in .env or dynamically via Home Assistant to enable water checking.
* **mqtt auto discovery:** in home assistant: need to change domains for entities and services (in lovelace cards, automations, scripts, ..) from light. to fan (lovelace, automations). Avoiding having 2 gardyn "lights" for easier distinction; pump feels more simliar to a fan than a light to me (spinny things)
* **light,pump:** Modified the behavior of main execution in both scripts to require command-line arguments, impacting existing automation setups.
* added api for pump, light, and distance

### Features

* Add light and water commands ([#81](https://github.com/iot-root/garden-of-eden/issues/81)) ([03faccf](https://github.com/iot-root/garden-of-eden/commit/03faccff45788bddc284c4cae8e744813c9a0074))
* add mqtt ([f227130](https://github.com/iot-root/garden-of-eden/commit/f227130de5578cc737a800914959b160a1f3a314))
* add mqtt service, update py requirements, remove unused code ([ff21619](https://github.com/iot-root/garden-of-eden/commit/ff21619dc333fa5b82a1ac9bfe4daffeb8e95aa4))
* add pcb-temp, pump power stats interface and rest api ([fa78c08](https://github.com/iot-root/garden-of-eden/commit/fa78c08f323b182c29ddd7f1e90989fdc3de8c6d))
* add water and light scripts for ease of use and crontab jobs ([03faccf](https://github.com/iot-root/garden-of-eden/commit/03faccff45788bddc284c4cae8e744813c9a0074))
* added api for pump, light, and distance ([f2a489b](https://github.com/iot-root/garden-of-eden/commit/f2a489b45fbe4250f33c8db35e7d8c2949331a83))
* added automations ([cf6c680](https://github.com/iot-root/garden-of-eden/commit/cf6c6803a10299b0d17328190b560b92d84ce2bd))
* added gh actions ([e6368c0](https://github.com/iot-root/garden-of-eden/commit/e6368c0c2749b192149e49388fada38dfc1926b4))
* added guard to routes, updated logging ([94315f3](https://github.com/iot-root/garden-of-eden/commit/94315f3888afa9866f10dc2a8b45295baae3c83a))
* allow app to start without i2c presence for sensors ([#44](https://github.com/iot-root/garden-of-eden/issues/44)) ([1c96f40](https://github.com/iot-root/garden-of-eden/commit/1c96f400718d364063243222b140db0c612ec825))
* **api:** add temp and humidity interface and API routes ([5e0bc9a](https://github.com/iot-root/garden-of-eden/commit/5e0bc9aabe594ef0d321548e13f799704b4133f7))
* **camera:** add support for periodic image capture and raw MQTT publishing ([3a4d9bb](https://github.com/iot-root/garden-of-eden/commit/3a4d9bb664c9199531de781a76539cee52c69769))
* humidity, temp , pcb_temp , light and pump working ([0aecbe1](https://github.com/iot-root/garden-of-eden/commit/0aecbe173979ec7633ea4dae30ee7f8cc80efba3))
* **light,pump:** add command-line args for light and pump control ([#48](https://github.com/iot-root/garden-of-eden/issues/48)) ([49ecc70](https://github.com/iot-root/garden-of-eden/commit/49ecc7066ae13e39ca1fe9277cf9f297fc9d5d15))
* limit user input ([31ce402](https://github.com/iot-root/garden-of-eden/commit/31ce40249a980b7ee4bbcdf281a6d3f1396441b8))
* **motor:** add get_speed method ([8e7835b](https://github.com/iot-root/garden-of-eden/commit/8e7835b488123c69855ff9a2b82363281c53687d))
* mqtt light working with homeassistant ([14fb6de](https://github.com/iot-root/garden-of-eden/commit/14fb6de6ef6dd82b3a69634a866e9c0aabfeca65))
* mqtt working for homeassistant ([b745616](https://github.com/iot-root/garden-of-eden/commit/b74561674b207f2cb74e81e4a2090def301a05ff))
* **mqtt:** add on demand sensor reading updates and fixed water level reading ([7a8a642](https://github.com/iot-root/garden-of-eden/commit/7a8a6425def3baa43fd39a9dc00564e54bd427f3))
* **mqtt:** add water low threshold checking and dynamic override ([65bbe34](https://github.com/iot-root/garden-of-eden/commit/65bbe3417e79afaf7f1fca94fc7165e57dbe1c01)), closes [#83](https://github.com/iot-root/garden-of-eden/issues/83)
* one button toggle light, two button press toggle pump ([832f9b4](https://github.com/iot-root/garden-of-eden/commit/832f9b4cd7be4054672e47016918b61a096515e1))
* **pump:** add code for pump on/off ([#17](https://github.com/iot-root/garden-of-eden/issues/17)) ([ec2e06d](https://github.com/iot-root/garden-of-eden/commit/ec2e06d6e38233e376be50e309f5add054a63276))
* **sensors:** add waterlevel interface close [#38](https://github.com/iot-root/garden-of-eden/issues/38) ([e3b83d2](https://github.com/iot-root/garden-of-eden/commit/e3b83d20cbae17b4c7e88c22eac326aa0ce9906a))
* **setup:** fix and streamline setup closes [#50](https://github.com/iot-root/garden-of-eden/issues/50) ([bbf006c](https://github.com/iot-root/garden-of-eden/commit/bbf006caed953eec1fde1f3d6b47ca9a6a8c4e4e))


### Bug Fixes

* add i2c address not found exception for ina219 pump curr monitor ([de753dd](https://github.com/iot-root/garden-of-eden/commit/de753dd4dc033bf09f7ee45019868633d9057697))
* add light entity for pump mqtt discovery topic ([a992d73](https://github.com/iot-root/garden-of-eden/commit/a992d7331c5e50e445f3352db1eee0ecf078c3da))
* add missing config variable IMAGE_INTERVAL_SECONDS to mqtt.py ([9efcd96](https://github.com/iot-root/garden-of-eden/commit/9efcd965023311a5e2a992369f30b8d3f9ae5cf1))
* add sudo for symlink creation in setup.sh ([1cf1674](https://github.com/iot-root/garden-of-eden/commit/1cf1674382aefe4e44918e863073a78488bab501))
* address issue with not reporting water level and enhance distance measurement ([735aaf6](https://github.com/iot-root/garden-of-eden/commit/735aaf652d3592fd60a330877f899afbf8baafec))
* cleanup and fix of bin/setup.sh ([a84f224](https://github.com/iot-root/garden-of-eden/commit/a84f2249051cf91f7e72799963395bfc09049ba9))
* convert IMAGE_INTERVAL_SECONDS to int in config.py ([662559a](https://github.com/iot-root/garden-of-eden/commit/662559a04f6f1c14deabe82179b6d05c39aee4f1))
* corrected variable in .env-dist ([8742f4f](https://github.com/iot-root/garden-of-eden/commit/8742f4fbba910cfb1784bc2668854b1d95037839))
* fix paths for data collector bin/get-sensor-data.sh ([88886a4](https://github.com/iot-root/garden-of-eden/commit/88886a4e9e11427a97bcac67f0cbb39aeed7cbcd))
* fix speed publish topic for pump ([8d083e0](https://github.com/iot-root/garden-of-eden/commit/8d083e0babbb7cc93f16266024c50ddaaa3b9cc5))
* handle failed distance reading ([85eba1d](https://github.com/iot-root/garden-of-eden/commit/85eba1d3bf8ba14b3f8057bf1637035f1c01cdac))
* **home assistant:** HA autom. entity domain ([13406e4](https://github.com/iot-root/garden-of-eden/commit/13406e40a764e6e6b6185b198796ca89122aff14))
* make light and water executable +x ([7128901](https://github.com/iot-root/garden-of-eden/commit/712890140bf74825edab426754fb6623422ba0ad))
* make sure pigpiod is running for mqtt service ([7f34509](https://github.com/iot-root/garden-of-eden/commit/7f345093ebbd3957448a024f773280cb605ef84a))
* on_connect function mqtt.py ([c71b08c](https://github.com/iot-root/garden-of-eden/commit/c71b08ceac56c4662f98c4f03bc285017d136178))
* **pump:** fix factory argument for pump.py ([b011227](https://github.com/iot-root/garden-of-eden/commit/b0112277b7001c82b5956d1717dc97c9f04d44c8))
* removed gh action for tests ([e8aebc7](https://github.com/iot-root/garden-of-eden/commit/e8aebc75ff56fd271bfe3292c3c869a08e569bb4))
* **sensor-interface:** water_level.py ([0227231](https://github.com/iot-root/garden-of-eden/commit/0227231bec6dfb6a1d3b3a72d549ffe5b861178f))
* update on_message function to handle binary data ([9e10b0f](https://github.com/iot-root/garden-of-eden/commit/9e10b0fdd858471005077718b201889698f4315e))
* updating gh actions ([581d0d3](https://github.com/iot-root/garden-of-eden/commit/581d0d3f0ed1d7b1603f5e0ac15dc5b7c4f201d4))
* updating gh actions ([c24885b](https://github.com/iot-root/garden-of-eden/commit/c24885bf06022e840455311d2ff95c07720f18ba))


### Documentation

* add test commands for mqtt broker setup ([6835306](https://github.com/iot-root/garden-of-eden/commit/6835306c4607a8cb9a082110b3aa6cd97eabb737))
* **contributors.md:** add contributor commit guide ([#21](https://github.com/iot-root/garden-of-eden/issues/21)) ([4fc1441](https://github.com/iot-root/garden-of-eden/commit/4fc14418ee49ad6b86ed2333642477796b7e3010))
* create license ([#20](https://github.com/iot-root/garden-of-eden/issues/20)) ([e249cc9](https://github.com/iot-root/garden-of-eden/commit/e249cc98dfbb33d442a51544007a2fcfea4817f6))
* fix type in README.md ([d33513b](https://github.com/iot-root/garden-of-eden/commit/d33513b8c1f12fb7f1378b6293369aaac7e1c093))
* update readme ([99b345d](https://github.com/iot-root/garden-of-eden/commit/99b345dabbb010b4d8ba26cb71f920562988229f))
* update readme ([1d71148](https://github.com/iot-root/garden-of-eden/commit/1d71148473f3c0aed6f30f64fd0ee54243feb71c))
* update readme and banner ([f2825a1](https://github.com/iot-root/garden-of-eden/commit/f2825a1cb08cc1e68928c501db782c65d4ac8b62))
* update readme and banner ([87e7fbf](https://github.com/iot-root/garden-of-eden/commit/87e7fbf922b5d8a43ae97f9bbf94dc1b4bd7dec5))
* update readme banner ([dce7327](https://github.com/iot-root/garden-of-eden/commit/dce73276e4e85aa46d10318704b5cdf8f3f99b31))
* update readme temp notes ([38d1bec](https://github.com/iot-root/garden-of-eden/commit/38d1bec3aaa008cee6f90d419c155043432bea8c))
* update readme with sensor details ([1e7ec39](https://github.com/iot-root/garden-of-eden/commit/1e7ec39281b45a24a3c757de0b980758671bb3ed))
* update README.md ([ff89248](https://github.com/iot-root/garden-of-eden/commit/ff89248067f303d0d55df50bc146b016e6ec0d79))
* update README.md for button presses ([1dba046](https://github.com/iot-root/garden-of-eden/commit/1dba0462e9db2c47bfb02317f3a267a29ded96b2))
* Updated README ([ad8e08a](https://github.com/iot-root/garden-of-eden/commit/ad8e08a2a2f10ee2e74b94acc1998933d117c4a9))
* Updated README ([40f935c](https://github.com/iot-root/garden-of-eden/commit/40f935c420503cacb0cb86576e21c666b7f0126e))
* updated README, Contributors and edited distance endpoint ([#53](https://github.com/iot-root/garden-of-eden/issues/53)) ([c225a62](https://github.com/iot-root/garden-of-eden/commit/c225a62eadb59b18eb54aae95dea0a04696d8b58))
* updated README.md with video tutorial link ([3c8e247](https://github.com/iot-root/garden-of-eden/commit/3c8e2474b79561f978b28df54ccee20b5e2ce7fb))


### Code Refactoring

* **mqtt auto discovery:** changed the pumps domain from light to fan ([#52](https://github.com/iot-root/garden-of-eden/issues/52)) ([0bc4cc8](https://github.com/iot-root/garden-of-eden/commit/0bc4cc8130d596e91a261b10b77e6ab504b8fbe7))

## Changelog

This file is maintained automatically by
[release-please](https://github.com/googleapis/release-please) from
[Conventional Commits](CONTRIBUTORS.md). Do not edit by hand below this line.

<!-- release-please-start -->
<!-- release-please-end -->
