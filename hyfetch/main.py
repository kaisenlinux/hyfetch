#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime
import json
import random
import traceback
from itertools import permutations
from math import ceil

from . import termenv, neofetch_util, pride_month
from .color_scale import Scale
from .color_util import clear_screen
from .constants import *
from .models import Config
from .neofetch_util import *
from .presets import PRESETS


def check_config(path) -> Config:
    """
    Check if the configuration exists. Return the config object if it exists. If not, call the
    config creator

    :return: Config object
    """
    if path.is_file():
        try:
            return Config.from_dict(json.loads(path.read_text('utf-8')))
        except KeyError:
            return create_config()

    return create_config()


def create_config() -> Config:
    """
    Create config interactively

    :return: Config object (automatically stored)
    """
    # Detect terminal environment (doesn't work on Windows)
    det_bg = termenv.get_background_color()
    det_ansi = termenv.detect_ansi_mode()

    asc = get_distro_ascii()
    asc_width, asc_lines = ascii_size(asc)
    logo = color("&l&bhyfetch&~&L" if det_bg is None or det_bg.is_light() else "&l&bhy&ffetch&~&L")
    title = f'Welcome to {logo} Let\'s set up some colors first.'
    clear_screen(title)

    option_counter = 1

    def update_title(k: str, v: str):
        nonlocal title, option_counter
        if not k.endswith(":"):
            k += ':'
        title += f"\n&e{option_counter}. {k.ljust(30)} &~{v}"
        option_counter += 1

    def print_title_prompt(prompt: str):
        printc(f'&a{option_counter}. {prompt}')

    ##############################
    # 0. Check term size
    try:
        term_len, term_lines = os.get_terminal_size().columns, os.get_terminal_size().lines
        term_len_min = 2 * asc_width + 4
        term_lines_min = 30
        if term_len < term_len_min or term_lines < term_lines_min:
            printc(f'&cWarning: Your terminal is too small ({term_len} * {term_lines}). \n'
                   f'Please resize it to at least ({term_len_min} * {term_lines_min}) for better experience.')
            input('Press enter to ignore...')
    except:
        # print('Warning: We cannot detect your terminal size.')
        pass

    ##############################
    # 1. Select color system
    def select_color_system():
        if det_ansi == 'rgb':
            return 'rgb', 'Detected color mode'

        clear_screen(title)
        term_len, term_lines = term_size()

        scale2 = Scale(['#12c2e9', '#c471ed', '#f7797d'])
        _8bit = [scale2(i / term_len).to_ansi_8bit(False) for i in range(term_len)]
        _rgb = [scale2(i / term_len).to_ansi_rgb(False) for i in range(term_len)]

        printc('&f' + ''.join(c + t for c, t in zip(_8bit, '8bit Color Testing'.center(term_len))))
        printc('&f' + ''.join(c + t for c, t in zip(_rgb, 'RGB Color Testing'.center(term_len))))

        print()
        print_title_prompt('Which &bcolor system &ado you want to use?')
        printc(f'(If you can\'t see colors under "RGB Color Testing", please choose 8bit)')
        print()

        return literal_input('Your choice?', ['8bit', 'rgb'], 'rgb'), 'Selected color mode'

    # Override global color mode
    color_system, ttl = select_color_system()
    GLOBAL_CFG.color_mode = color_system
    update_title(ttl, color_system)

    ##############################
    # 2. Select light/dark mode
    def select_light_dark():
        if det_bg is not None:
            return det_bg.is_light(), 'Detected background color'

        clear_screen(title)
        inp = literal_input(f'2. Is your terminal in &blight mode&~ or &4dark mode&~?',
                            ['light', 'dark'], 'dark')
        return inp == 'light', 'Selected background color'

    is_light, ttl = select_light_dark()
    light_dark = 'light' if is_light else 'dark'
    GLOBAL_CFG.is_light = is_light
    update_title(ttl, light_dark)

    ##############################
    # 3. Choose preset
    # Create flags = [[lines]]
    flags = []
    spacing = max(max(len(k) for k in PRESETS.keys()), 20)
    for name, preset in PRESETS.items():
        flag = preset.color_text(' ' * spacing, foreground=False)
        flags.append([name.center(spacing), flag, flag, flag])

    # Calculate flags per row
    flags_per_row = term_size()[0] // (spacing + 2)
    row_per_page = max(1, (term_size()[1] - 13) // 5)
    num_pages = ceil(len(flags) / (flags_per_row * row_per_page))

    # Create pages
    pages = []
    for i in range(num_pages):
        page = []
        for j in range(row_per_page):
            page.append(flags[:flags_per_row])
            flags = flags[flags_per_row:]
            if not flags:
                break
        pages.append(page)

    def print_flag_page(page: list[list[list[str]]], page_num: int):
        clear_screen(title)
        print_title_prompt("Let's choose a flag!")
        printc('Available flag presets:')
        print(f'Page: {page_num + 1} of {num_pages}')
        print()
        for i in page:
            print_flag_row(i)
        print()

    def print_flag_row(current: list[list[str]]):
        [printc('  '.join(line)) for line in zip(*current)]
        print()

    page = 0
    while True:
        print_flag_page(pages[page], page)

        tmp = PRESETS['rainbow'].set_light_dl_def(light_dark).color_text('preset')
        opts = list(PRESETS.keys())
        if page < num_pages - 1:
            opts.append('next')
        if page > 0:
            opts.append('prev')
        print("Enter 'next' to go to the next page and 'prev' to go to the previous page.")
        preset = literal_input(f'Which {tmp} do you want to use? ', opts, 'rainbow', show_ops=False)
        if preset == 'next':
            page += 1
        elif preset == 'prev':
            page -= 1
        else:
            _prs = PRESETS[preset]
            update_title('Selected flag', _prs.set_light_dl_def(light_dark).color_text(preset))
            break

    #############################
    # 4. Dim/lighten colors
    def select_lightness():
        clear_screen(title)
        print_title_prompt("Let's adjust the color brightness!")
        printc(f'The colors might be a little bit too {"bright" if is_light else "dark"} for {light_dark} mode.')
        print()

        # Print cats
        num_cols = (term_size()[0] // (TEST_ASCII_WIDTH + 2)) or 1
        mn, mx = 0.15, 0.85
        ratios = [col / num_cols for col in range(num_cols)]
        ratios = [(r * (mx - mn) / 2 + mn) if is_light else ((r * (mx - mn) + (mx + mn)) / 2) for r in ratios]
        lines = [ColorAlignment('horizontal').recolor_ascii(TEST_ASCII.replace(
            '{txt}', f'{r * 100:.0f}%'.center(5)), _prs.set_light_dl(r, light_dark)).split('\n') for r in ratios]
        [printc('  '.join(line)) for line in zip(*lines)]

        def_lightness = GLOBAL_CFG.default_lightness(light_dark)

        while True:
            print()
            printc(f'Which brightness level looks the best? (Default: {def_lightness * 100:.0f}% for {light_dark} mode)')
            lightness = input('> ').strip().lower() or None

            # Parse lightness
            if not lightness or lightness in ['unset', 'none']:
                return def_lightness

            try:
                lightness = int(lightness[:-1]) / 100 if lightness.endswith('%') else float(lightness)
                assert 0 <= lightness <= 1
                return lightness

            except Exception:
                printc('&cUnable to parse lightness value, please input it as a decimal or percentage (e.g. 0.5 or 50%)')

    lightness = select_lightness()
    _prs = _prs.set_light_dl(lightness, light_dark)
    update_title('Selected Brightness', f"{lightness:.2f}")

    #############################
    # 5. Color arrangement
    color_alignment = None
    fore_back = get_fore_back()

    # Calculate amount of row/column that can be displayed on screen
    ascii_per_row = max(1, term_size()[0] // (asc_width + 2))
    ascii_rows = max(1, (term_size()[1] - 8) // asc_lines)

    # Displays horizontal and vertical arrangements in the first iteration, but hide them in
    # later iterations
    hv_arrangements = [
        ('Horizontal', ColorAlignment('horizontal', fore_back=fore_back)),
        ('Vertical', ColorAlignment('vertical'))
    ]
    arrangements = hv_arrangements.copy()

    # Loop for random rolling
    while True:
        clear_screen(title)

        # Random color schemes
        pis = list(range(len(_prs.unique_colors().colors)))
        slots = list(set(re.findall('(?<=\\${c)[0-9](?=})', asc)))
        while len(pis) < len(slots):
            pis += pis
        perm = {p[:len(slots)] for p in permutations(pis)}
        random_count = max(0, ascii_per_row * ascii_rows - len(arrangements))
        if random_count > len(perm):
            choices = perm
        else:
            choices = random.sample(sorted(perm), random_count)
        choices = [{slots[i]: n for i, n in enumerate(c)} for c in choices]
        arrangements += [(f'random{i}', ColorAlignment('custom', r)) for i, r in enumerate(choices)]
        asciis = [[*ca.recolor_ascii(asc, _prs).split('\n'), k.center(asc_width)] for k, ca in arrangements]

        while asciis:
            current = asciis[:ascii_per_row]
            asciis = asciis[ascii_per_row:]

            # Print by row
            [printc('  '.join(line)) for line in zip(*current)]
            print()

        print_title_prompt("Let's choose a color arrangement!")
        printc(f'You can choose standard horizontal or vertical alignment, or use one of the random color schemes.')
        print('You can type "roll" to randomize again.')
        print()
        choice = literal_input(f'Your choice?', ['horizontal', 'vertical', 'roll'] + [f'random{i}' for i in range(random_count)], 'horizontal')

        if choice == 'roll':
            arrangements = []
            continue

        # Save choice
        arrangement_index = {k.lower(): ca for k, ca in hv_arrangements + arrangements}
        if choice in arrangement_index:
            color_alignment = arrangement_index[choice]
        else:
            print('Invalid choice.')
            continue

        break

    update_title('Color alignment', color_alignment)

    # Create config
    clear_screen(title)
    c = Config(preset, color_system, light_dark, lightness, color_alignment)

    # Save config
    print()
    save = literal_input(f'Save config?', ['y', 'n'], 'y')
    if save == 'y':
        c.save()

    return c


def create_parser() -> argparse.ArgumentParser:
    # Create CLI
    hyfetch = color('&l&bhyfetch&~&L')
    parser = argparse.ArgumentParser(description=color(f'{hyfetch} - neofetch with flags <3'), prog="hyfetch")

    parser.add_argument('-c', '--config', action='store_true', help=color(f'Configure hyfetch'))
    parser.add_argument('-C', '--config-file', dest='config_file', default=CONFIG_PATH, help=f'Use another config file')
    parser.add_argument('-p', '--preset', help=f'Use preset', choices=list(PRESETS.keys()))
    parser.add_argument('-m', '--mode', help=f'Color mode', choices=['8bit', 'rgb'])
    parser.add_argument('-b', '--backend', help=f'Choose a *fetch backend', choices=['qwqfetch', 'neofetch', 'fastfetch', 'fastfetch-old'])
    parser.add_argument('--args', help=f'Additional arguments pass-through to backend')
    parser.add_argument('--c-scale', dest='scale', help=f'Lighten colors by a multiplier', type=float)
    parser.add_argument('--c-set-l', dest='light', help=f'Set lightness value of the colors', type=float)
    parser.add_argument('--c-overlay', action='store_true', dest='overlay', help=f'Use experimental overlay color adjusting instead of HSL lightness')
    parser.add_argument('-V', '--version', dest='version', action='store_true', help=f'Check version')
    parser.add_argument('--june', action='store_true', help=f'Show pride month easter egg')
    parser.add_argument('--debug', action='store_true', help=f'Debug mode')

    parser.add_argument('--distro', '--test-distro', dest='distro', help=f'Test for a specific distro')
    parser.add_argument('--ascii-file', help='Use a specific file for the ascii art')

    # Hidden debug arguments
    # --test-print: Print the ascii distro and exit
    parser.add_argument('--test-print', action='store_true', help=argparse.SUPPRESS)
    # --ask-exit: Ask for input before exiting
    parser.add_argument('--ask-exit', action='store_true', help=argparse.SUPPRESS)

    return parser


def run():
    # Optional: Import readline
    try:
        import readline
    except ModuleNotFoundError:
        pass

    # On Windows: Try to fix color rendering if not in git bash
    if IS_WINDOWS:
        import colorama
        colorama.just_fix_windows_console()

    parser = create_parser()
    args = parser.parse_args()

    # Use a custom distro
    GLOBAL_CFG.override_distro = args.distro
    GLOBAL_CFG.use_overlay = args.overlay

    if args.version:
        print(f'Version is {VERSION}')
        return

    # Ensure git bash for windows
    ensure_git_bash()
    check_windows_cmd()

    if args.debug:
        GLOBAL_CFG.debug = True

    if args.test_print:
        print(get_distro_ascii())
        return

    # Check if user provided alternative config path
    if not args.config_file == CONFIG_PATH:
        args.config_file = Path(os.path.abspath(args.config_file))

        # If provided file does not exist use default config
        if not args.config_file.is_file():
            args.config_file = CONFIG_PATH

    # Load config or create config
    config = create_config() if args.config else check_config(args.config_file)

    # Check if it's June (pride month)
    now = datetime.datetime.now()
    june_path = CACHE_PATH / f'animation-displayed-{now.year}'
    if now.month == 6 and now.year not in config.pride_month_shown and not june_path.is_file() and os.isatty(sys.stdout.fileno()):
        args.june = True

    if args.june and not config.pride_month_disable:
        pride_month.start_animation()
        print()
        print("Happy pride month!")
        print("(You can always view the animation again with `hyfetch --june`)")
        print()

        if not june_path.is_file():
            june_path.parent.mkdir(parents=True, exist_ok=True)
            june_path.touch()

    # Use a custom distro
    GLOBAL_CFG.override_distro = args.distro or config.distro

    # Param overwrite config
    if args.preset:
        config.preset = args.preset
    if args.mode:
        config.mode = args.mode
    if args.backend:
        config.backend = args.backend
    if args.args:
        config.args = args.args

    # Override global color mode
    GLOBAL_CFG.color_mode = config.mode
    GLOBAL_CFG.is_light = config.light_dark == 'light'

    # Get preset
    preset = PRESETS.get(config.preset)

    # Lighten (args > config)
    if args.scale:
        preset = preset.lighten(args.scale)
    elif args.light:
        preset = preset.set_light_raw(args.light)
    else:
        preset = preset.set_light_dl(config.lightness or GLOBAL_CFG.default_lightness())

    # Run
    try:
        asc = get_distro_ascii() if not args.ascii_file else Path(args.ascii_file).read_text("utf-8")
        asc = config.color_align.recolor_ascii(asc, preset)
        neofetch_util.run(asc, config.backend, config.args or '')
    except Exception as e:
        print(f'Error: {e}')
        traceback.print_exc()

    if args.ask_exit:
        input('Press any key to exit...')
