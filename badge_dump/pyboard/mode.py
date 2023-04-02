# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

import screen
import counters
import rgb
import prng
import network
import logogen
import browser
import adventure

MAIN_MENU_MODE = 0
NETWORK_MODE = 1
IDLE_MODE = 2
BADGE_ADVENTURE_MODE = 3
LOGO_GENERATOR_MODE = 4
BROWSER_ENTRY_MODE = 5
SYSTEM_MENU_MODE = 6
BROWSER_HOMEPAGE_MODE = 7
BROWSING_MODE = 8
URL_ENTRY_MODE = 9
SETTINGS_MENU_MODE = 10
VERIFY_MODE = 11

ui_color = 0
last_ui_color = 0

ui_mode = 0
verify_type = 0
before_idle = 0
idle_mode_setting = 0
idle_entry_type = 0
to_idle_counter_index = 0
to_next_counter_index = 0

def initialize():
    global to_idle_counter_index, to_next_counter_index
    to_idle_counter_index = counters.start(100000)
    to_next_counter_index = counters.start(600)
    # or for faster idle / next idle timeouts use the below instead
    #to_idle_counter_index = counters.start(12000)
    #to_next_counter_index = counters.start(100)

def start(mode):
    global ui_mode, before_idle
    print('mode: starting: ' + str(mode))
    if mode == MAIN_MENU_MODE:
        print('mode: starting MAIN_MENU_MODE')
        ui_mode = MAIN_MENU_MODE
        screen.render_file('graphics/mainmenu.tcipage')

    elif mode == NETWORK_MODE:
        print('mode: starting NETWORK_MODE')
        before_idle = ui_mode
        ui_mode = NETWORK_MODE
        screen.render_file('graphics/networkmode.tcipage')

    elif mode == IDLE_MODE:
        print('mode: starting IDLE_MODE')
        before_idle = ui_mode
        ui_mode = IDLE_MODE
        next_idle_screen()

    elif mode == BADGE_ADVENTURE_MODE:
        print('mode: starting BADGE_ADVENTURE_MODE')
        ui_mode = BADGE_ADVENTURE_MODE
        adventure.start_badge_adventure()

    elif mode == LOGO_GENERATOR_MODE:
        print('mode: starting LOGO_GENERATOR_MODE')
        ui_mode = LOGO_GENERATOR_MODE
        screen.render_file('graphics/logogen.tcipage')

    elif mode == BROWSER_ENTRY_MODE:
        print('mode: starting BROWSER_ENTRY_MODE')
        browser.clear_tree()
        ui_mode = URL_ENTRY_MODE
        browser.print_url_options()

    elif mode == SYSTEM_MENU_MODE:
        print('mode: starting SYSTEM_MENU_MODE')
        ui_mode = SYSTEM_MENU_MODE
        screen.render_file('graphics/systemmenu.tcipage')

    elif mode == BROWSER_HOMEPAGE_MODE:
        print('mode: starting BROWSER_HOMEPAGE_MODE')
        ui_mode = BROWSER_HOMEPAGE_MODE
        browser.browser_address = 700
        browser.browser_page = 0
        browser.prerender_site()

    elif mode == URL_ENTRY_MODE:
        print('mode: starting URL_ENTRY_MODE')
        browser.print_url_options()

    elif mode == BROWSING_MODE:
        print('mode: starting BROWSING_MODE')
        browser.update_browser()

    elif mode == SETTINGS_MENU_MODE:
        print('mode: starting SETTINGS_MENU_MODE')
        ui_mode = SETTINGS_MENU_MODE
        if idle_mode_setting == 0:
            screen.render_file('graphics/settingsmenu.tcipage', modifiers = [212, 31])
        elif idle_mode_setting == 1:
            screen.render_file('graphics/settingsmenu.tcipage', modifiers = [272, 31])
        elif idle_mode_setting == 2:
            screen.render_file('graphics/settingsmenu.tcipage', modifiers = [332, 31])
        elif idle_mode_setting == 3:
            screen.render_file('graphics/settingsmenu.tcipage', modifiers = [392, 31])
        else:
            screen.render_file('graphics/settingsmenu.tcipage')

    elif mode == VERIFY_MODE:
        print('mode: starting VERIFY_MODE verify_type: ' + str(verify_type))
        ui_mode = VERIFY_MODE
        if verify_type == 1: # save logo
            screen.render_arttext('Are you sure? This will replace the logo file in your player file with the current state of the Logo Generator screen [r]yes [g]no')
        elif verify_type == 2: # player reset
            screen.render_arttext('Are you sure? This will replace your player file with a factory default version [r]yes [g]no')
        elif verify_type == 3: # factory reset
            screen.render_arttext('Are you sure? This will replace your player file with a default version and will generate 700 imaginary friends, overwriting any ghosts you have collected over the badge network [r]yes [g]no')
        elif verify_type == 4: # update site from eeprom
            screen.render_arttext('Are you sure? This will replace the website and or logo presently stored in your player file with custom versions which you have uploaded to your badge eeprom root directory (custom.tcisite and/or custom.tcipage) [r]yes [g]no')

def encoder_click_event():
    global verify_type
    print('mode: click: ' + ('black', 'white', 'red', 'yellow', 'green', 'teal', 'blue', 'violet')[ui_color])

    if ui_mode == MAIN_MENU_MODE:
        if ui_color == 0:
            pass
        elif ui_color == 1:
            start(NETWORK_MODE)
        else:
            main_menu_click(ui_color - 2)

    elif ui_mode == SYSTEM_MENU_MODE:
        if ui_color == 0:
            start(MAIN_MENU_MODE)
        elif ui_color == 1:
            start(NETWORK_MODE)
        else:
            system_menu_click(ui_color - 2)

    elif ui_mode == IDLE_MODE:
        resume()
    elif ui_mode == NETWORK_MODE:
        resume()

    elif ui_mode == BADGE_ADVENTURE_MODE:
        if ui_color == 0:
            start(MAIN_MENU_MODE)
        elif ui_color == 1:
            start(NETWORK_MODE)
        else:
            adventure.badge_adventure_click(ui_color - 2)

    elif ui_mode == LOGO_GENERATOR_MODE:
        if ui_color == 0:
            start(MAIN_MENU_MODE)
        elif ui_color == 1:
            start(NETWORK_MODE)
        else:
            logogen.logogen_click(ui_color - 2)

    elif ui_mode == BROWSING_MODE:
        if ui_color == 0:
            start(MAIN_MENU_MODE)
        elif ui_color == 1:
            start(NETWORK_MODE)
        else:
            browser.browser_click(ui_color - 2)

    elif ui_mode == URL_ENTRY_MODE:
        if ui_color == 0:
            start(MAIN_MENU_MODE)
        elif ui_color == 1:
            start(NETWORK_MODE)
        else:
            browser.url_entry_click(ui_color - 2)

    elif ui_mode == SETTINGS_MENU_MODE:
        if ui_color == 0:
            start(MAIN_MENU_MODE)
        elif ui_color == 1:
            start(NETWORK_MODE)
        else:
            settings_menu_click(ui_color - 2)

    elif ui_mode == VERIFY_MODE:
        if ui_color == 0:
            verify_type = 0
            start(MAIN_MENU_MODE)
        elif ui_color == 1:
            verify_type = 0
            start(NETWORK_MODE)
        else:
            verify_click(ui_color - 2)

def main_menu_click(user_input):
    global idle_entry_type
    print('mode: main_menu_click user_input: ' + str(user_input))
    if user_input == 0:
        start(BADGE_ADVENTURE_MODE)
    elif user_input == 1:
        start(BROWSER_HOMEPAGE_MODE)
    elif user_input == 2:
        start(BROWSER_ENTRY_MODE)
    elif user_input == 3:
        start(LOGO_GENERATOR_MODE)
    elif user_input == 4:
        start(SYSTEM_MENU_MODE)
    elif user_input == 5:
        idle_entry_type = 0
        start(IDLE_MODE)

def system_menu_click(user_input):
    global idle_entry_type, verify_type
    print('mode: system_menu_click user_input: ' + str(user_input))
    if user_input == 0: # cypher sleep
        idle_entry_type = 1
        start(IDLE_MODE)
    elif user_input == 1: # my logo sleep
        idle_entry_type = 2
        start(IDLE_MODE)
    elif user_input == 2: # idle settings
        start(SETTINGS_MENU_MODE)
    elif user_input == 3: # update site from eeprom
        verify_type = 4
        start(VERIFY_MODE)
    elif user_input == 4: # player reset
        verify_type = 2
        start(VERIFY_MODE)
    elif user_input == 5: # factory reset
        verify_type = 3
        start(VERIFY_MODE)

def settings_menu_click(user_input):
    global idle_mode_setting
    print('mode: settings_menu_click user_input: ' + str(user_input))
    if user_input == 0: # cyphercon logo
        print('mode: settings_menu_click setting to "cyphercon logo mode"')
        idle_mode_setting = 0
        start(SETTINGS_MENU_MODE)
    elif user_input == 1: # network logo
        print('mode: settings_menu_click setting to "network logo mode"')
        idle_mode_setting = 1
        start(SETTINGS_MENU_MODE)
    elif user_input == 2: # random logo
        print('mode: settings_menu_click setting to "random logo mode"')
        idle_mode_setting = 2
        start(SETTINGS_MENU_MODE)
    elif user_input == 3: # my logo
        print('mode: settings_menu_click setting to "my logo mode"')
        idle_mode_setting = 3
        start(SETTINGS_MENU_MODE)

def verify_click(user_input):
    global verify_type
    if user_input == 0: # [r] YES
        if verify_type == 1: # save logo
            verify_type = 0
            print('mode: saving logo to player file')
            logo_save(adventure.player_id)
            start(MAIN_MENU_MODE)
        if verify_type == 2: # player reset
            verify_type = 0
            print('mode: resetting player file to factory default')
            network.player_reset()
            start(MAIN_MENU_MODE)
        if verify_type == 3: # factory reset
            verify_type = 0
            print('mode: resetting badge to factory default, this may take a while')
            network.factory_reset()
            start(MAIN_MENU_MODE)
        if verify_type == 4: # update from eeprom
            verify_type = 0
            print('mode: loading custom.tcisite and/or custom.tcipage from eeprom root')
            network.apply_updates_from_eeprom()
            start(MAIN_MENU_MODE)

    else: # [g] (or anything else for that matter) NO
        verify_type = 0
        start(MAIN_MENU_MODE)

def logo_save(player_id):
    print('logogen: saving logo to userfile: ' + str(player_id))
    adventure.unpack_user_key_to_disk(player_id)
    adventure.unpack_user_site_to_disk(player_id)
    logogen.logogen_reload()
    adventure.screen_to_temp()
    adventure.pack_user_file(player_id)

def resume(): # come back from idle or network mode
    global ui_mode
    print('mode: resuming from idle')
    ui_mode = before_idle
    rgb.wake_up_animation()
    start(before_idle)

def next_idle_screen():
    global idle_entry_type
    print('mode: idle_mode_setting: ' + str(idle_mode_setting) + ' idle_entry_type: ' + str(idle_entry_type))
    if idle_entry_type == 0: # timed out / main menu sleep
        if idle_mode_setting == 0: # cyphercon logo
            screen.render_file('graphics/cyphercon6.tcipage')
            idle_entry_type = 3
        elif idle_mode_setting == 1: # logo from network collected logo
            count = 0
            ghost_id = 0
            while(True): # go ghost hunting to find real user files that came in over the network
                ghost_id = prng.step(rgb.rgb_prng, 0, 700)
                count = count + 1
                if count >= 700: # this house is clear, only try 700 times
                    break
                version = network.get_version(ghost_id)
                if version > 1:
                    break
            adventure.unpack_user_logo_to_disk(ghost_id)
            screen.render_file('temp/loaded.tcipage')
        elif idle_mode_setting == 2: # random logo
            logogen.logogen_random_for_idle()
        elif idle_mode_setting == 3: # logo from my user file logo
            # load my logo
            adventure.unpack_user_logo_to_disk(adventure.player_id)
            screen.render_file('temp/loaded.tcipage')
            idle_entry_type = 3
    elif idle_entry_type == 1: # system menu cypercon sleep, first time
        screen.render_file('graphics/cyphercon6.tcipage')
        idle_entry_type = 3
    elif idle_entry_type == 2: # system menu my logo sleep, first time
        # load my logo
        adventure.unpack_user_logo_to_disk(adventure.player_id)
        screen.render_file('temp/loaded.tcipage')
        idle_entry_type = 3
    elif idle_entry_type == 3: # no new screens on future idle cycles
        pass
