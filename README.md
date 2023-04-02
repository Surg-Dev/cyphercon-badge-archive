# cyphercon-badge-archive
This repo contains a dump of the badge's FS, and the tools & documentation that VIPs held. The badge's user profile has an exploit, making it a polyglot to be executed in the browser of the badge. For more information, see our [writeup here](surg.dev/cyphercon23).

- `badge_dump` is a vaguely fresh dump of a badge. The cache and additional user profiles have been cleared, however.
- `documentation` stores docs on Dogteeth, the custom programming language and other specifications for the badge.
- `special 16mb micropython` has a micropython firmware file for Pico's with 16mb of eeprom, as the "Pico Boot" was used for the badges.
- `tools` have custom tools to make logos and adventures, along with the custom font used on the badges.
