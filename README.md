# Home Assistant integration for Unisenza Plus

Unisenza Plus is an IoT family that connects smart thermostats and other devices manufactured by [Purmo](https://global.purmo.com/>) to a cloud service via the Unisenza Plus Gateway.

This integration exposes the smart thermostats controlled via the cloud service as [climate entities](https://www.home-assistant.io/integrations/climate/).

## Pre-requisites

To use the integration, you need to create an account for the Unisenza Plus cloud service ([Google Play](https://play.google.com/store/apps/details?id=com.unisenzaplus.app&hl=en&gl=US), [Apple Store](https://apps.apple.com/us/app/unisenza-plus/id6444507262)). You need to have connected your smart thermostats to the cloud service via the [Unisenza Plus Gateway](https://global.purmo.com/en/products/heating-controls/electronic-heating-controls/communication/gateways-and-modems/unisenza-plus-gateway).

The following devices have been tested, and are known to work with the integration:

* Yali D+ radiators

## Installing

The easiest way to install the integration is via [HACS](https://hacs.xyz/). The integration is not (yet) listed as a default repository, and needs to be installed as a custom repository.

The integration is configured by providing the Unisenza Plus account credentials. On startup, the integration will find the gateway and thermostats connected to the cloud service, and expose them as devices and climate entities, respectively.

## Contributing

If you want to support new devices or features, please open an issue or PR in the [GitHub](https://github.com/jasujm/home-assistant-unisenza-plus) repository. New features and devices will likely also need changes to the [pyupgw](https://github.com/jasujm/pyupgw) library.

The integration has been developed with no access to the official documentation and only supports the devices that the author has available. To help inspect messages between the client and the cloud service, the pyupgw library includes a command-line interface with logging capabilities. See the [documentation](https://pyupgw.readthedocs.io/en/latest/developing.html) for more details.

## Disclaimer

The author of this integration is not affiliated with Purmo, the vendor of Unisenza Plus, in any way. The integration and its conformance to the Unisenza Plus API is implemented on a best-effort basis. No warranty of any kind is provided.
