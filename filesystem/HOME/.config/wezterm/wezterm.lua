-- Notes:
-- - pane.current_working_dir returns an URL object
--   everything after # in URL's are ommitted, meaning file paths may be cut off

local wezterm = require 'wezterm'
local os = require 'os'
local config = {}

-- https://wezterm.org/config/lua/config/hyperlink_rules.html
config.hyperlink_rules = wezterm.default_hyperlink_rules()

config.font = wezterm.font("Fira Code Nerd Font")
config.font_size = 19

-- this scrolls tabs *anywhere*
-- config.mouse_wheel_scrolls_tabs = true

local colours = {
    accent = "#FF4500",
    white = "#FFFFFF",
    black = "#000000",
    dark_grey = "#111111",
    dark_grey_highlight = "#360e00",
    grey = "#222222",
}

config.colors = {
    foreground = colours.white,
    background = colours.dark_grey,
    cursor_bg = colours.white,
    -- 	selection_fg = "#FFFFFF",
    selection_bg = colours.dark_grey_highlight,
    tab_bar = {
        inactive_tab_edge = colours.black, -- just hide it
        -- background = "#FF4500",
        active_tab = {
            bg_color = colours.accent,
            fg_color = colours.black,
        },
        inactive_tab = {
            bg_color = colours.dark_grey,
            fg_color = colours.accent,
        },
        inactive_tab_hover = {
            bg_color = colours.dark_grey,
            fg_color = colours.accent,
        },
        new_tab = {
            bg_color = colours.grey,
            fg_color = colours.accent,
        },
        new_tab_hover = {
            bg_color = colours.grey,
            fg_color = colours.white,
        },
    },
    ansi = {
        '#000000',
        '#aa0000',
        '#00aa00',
        '#aaaa00',
        '#00aaff',
        '#aa00aa',
        '#00aaaa',
        '#aaaaaa',
    },
    brights = {
        '#686868',
        '#ff0000',
        '#00ff00',
        '#ffff00',
        '#0000ff',
        '#ff00ff',
        '#00ffff',
        '#ffffff',
    },
    scrollbar_thumb = '#444444',
}

-- this only uses terminal characters for tabs
config.use_fancy_tab_bar = false
config.tab_max_width = 1024 -- just let the tab format be what it needs to be
config.hide_tab_bar_if_only_one_tab = true
config.window_frame = {
    -- font = wezterm.font "Fira Code Nerd Font Retina",
    active_titlebar_bg = colours.grey,
    inactive_titlebar_bg = colours.grey,
}

-- would disable in KWin rule anyway
config.window_decorations = "None"
config.window_padding = {
    left = 0,
    right = 0,
    top = 0,
    bottom = 0,
}

local act = wezterm.action
config.keys = {
    { key = 'LeftArrow',  mods = 'ALT|SHIFT', action = act.ActivateTabRelative(-1) },
    { key = 'RightArrow', mods = 'ALT|SHIFT', action = act.ActivateTabRelative(1) },
    {
        key = 'K',
        mods = 'CTRL|SHIFT',
        action = act.Multiple {
            act.ClearScrollback 'ScrollbackAndViewport',
            act.SendKey { key = 'L', mods = 'CTRL' },
        },
    },
    { key = 'LeftArrow',  mods = 'CTRL',       action = act.SendString '\x1b\x5b1;5D' },
    { key = 'RightArrow', mods = 'CTRL',       action = act.SendString '\x1b\x5b1;5C' },
    { key = 'm',          mods = 'CTRL|SHIFT', action = act.Nop },
    { key = '{',          mods = 'ALT|SHIFT',  action = act.SplitVertical({ domain = "CurrentPaneDomain" }) },
    { key = '}',          mods = 'ALT|SHIFT',  action = act.SplitHorizontal({ domain = "CurrentPaneDomain" }) },
    { key = 'w',          mods = 'ALT|SHIFT',  action = act.CloseCurrentPane { confirm = true } },
    { key = 'UpArrow',    mods = 'CTRL|SHIFT', action = act.ActivatePaneDirection 'Up' },
    { key = 'DownArrow',  mods = 'CTRL|SHIFT', action = act.ActivatePaneDirection 'Down' },
    { key = 'LeftArrow',  mods = 'CTRL|SHIFT', action = act.ActivatePaneDirection 'Left' },
    { key = 'RightArrow', mods = 'CTRL|SHIFT', action = act.ActivatePaneDirection 'Right' },
    { key = 'X',          mods = 'CTRL|SHIFT', action = act.Nop },
    { key = '0',          mods = 'ALT',        action = act.ActivateTab(9), }, -- extended later
    -- { key = 'F11', mods = '', action = act.ToggleFullScreen }, -- is this necessary?
}

config.mouse_bindings = {
    {
        event = { Up = { streak = 1, button = 'Left' } },
        mods = 'CTRL',
        action = act.OpenLinkAtMouseCursor,
    },
    {
        event = { Down = { streak = 1, button = 'Middle' } },
        action = act.PasteFrom 'Clipboard'
    },
    {
        event = { Down = { streak = 1, button = { WheelUp = 1 } } },
        alt_screen = false,
        mods = 'NONE',
        action = act.ScrollByLine(-3),
    },
    {
        event = { Down = { streak = 1, button = { WheelDown = 1 } } },
        alt_screen = false,
        mods = 'NONE',
        action = act.ScrollByLine(3),
    },
}

for i = 1, 9 do
    -- ALT + number to activate that tab
    table.insert(config.keys, {
        key = tostring(i),
        mods = 'ALT',
        action = act.ActivateTab(i - 1),
    })
end

-- DO NOT USE THIS
-- this solution is broken, it only effects the *first* window
-- the 'wezterm' package is bad, use 'AUR:wezterm-git'
-- local mux = wezterm.mux
-- wezterm.on("gui-startup", function(cmd)
-- 	local _, _, window = mux.spawn_window(cmd or {})
-- 	window:gui_window():maximize()
-- end)
-- config.initial_cols = 190
-- config.initial_rows = 50

-- Equivalent to POSIX basename(3)
-- Given "/foo/bar" returns "bar"
-- Given "c:\\foo\\bar" returns "bar"

local function basename(s)
    return string.gsub(s, '(.*[/])(.*)', '%2')
end

local user_name = os.getenv('USER')
wezterm.on('format-tab-title', function(tab, tabs, panes, config, hover, max_width)
    local pane = tab.active_pane

    local process = basename(pane.foreground_process_name)

    local cwd = pane.current_working_dir

    local path
    if cwd == nil then
        return { { Text = '-|-' } }
    else
        path = basename(cwd.file_path)
    end

    if path == user_name then
        path = '~ '
    end

    return tab.tab_index + 1 .. ': ' .. path .. '> ' .. process .. ' |'
end)
wezterm.on('format-window-title', function(tab, pane, tabs, panes, config)
    local pane = tab.active_pane

    local process = basename(pane.foreground_process_name)

    local cwd = pane.current_working_dir

    local path
    if cwd == nil then
        return 'wezterm'
    else
        path = basename(cwd.file_path)
    end

    if path == user_name then
        path = '~ '
    end

    return path .. '> ' .. process
end)

-- enable scroll bar, but only show if necessary
-- config.enable_scroll_bar = true
-- wezterm.on("update-status", function(window, pane)
-- 	local overrides = window:get_config_overrides() or {}
-- 	local dimensions = pane:get_dimensions()

-- 	overrides.enable_scroll_bar = dimensions.scrollback_rows > dimensions.viewport_rows and not pane:is_alt_screen_active()

-- 	window:set_config_overrides(overrides)
-- end)

return config
