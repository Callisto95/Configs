local wezterm = require 'wezterm'
local os = require 'os'
local config = {}

-- https://wezterm.org/config/lua/config/hyperlink_rules.html
config.hyperlink_rules = wezterm.default_hyperlink_rules()

config.font = wezterm.font("Fira Code Nerd Font")
config.font_size = 19

-- this scrolls tabs *anywhere*
-- config.mouse_wheel_scrolls_tabs = true

config.colors = {
	foreground = "#FFFFFF",
	background = "#222222",
	cursor_bg = "#FFFFFF",
-- 	selection_fg = "#FFFFFF",
	selection_bg = "#360e00",
	tab_bar = {
		inactive_tab_edge = "#161616",
		-- background = "#FF4500",
		active_tab = {
			bg_color = "#222222",
			fg_color = "#FF4500",
		},
		inactive_tab = {
			bg_color = "#050505",
			fg_color = "#FFFFFF",
		},
		inactive_tab_hover = {
			bg_color = "#161616",
			fg_color = "#FFFFFF",
		},
		new_tab = {
			bg_color = "#444444",
			fg_color = "#FF4500",
		},
		new_tab_hover = {
			bg_color = "#444444",
			fg_color = "#FFFFFF",
		}
	},
	ansi = {
		'#000000',
		'#b21818',
		'#18b218',
		'#cece00',
		'#0066ff',
		'#b218b2',
		'#18b2b2',
		'#b2b2b2',
	},
	brights = {
		'#686868',
		'#ff5454',
		'#54ff54',
		'#ffff54',
		'#5454ff',
		'#ff54ff',
		'#54ffff',
		'#ffffff',
	},
	scrollbar_thumb = '#444444',
}

config.window_frame = {
	font = wezterm.font "Fira Code Retina",
	active_titlebar_bg = "#444444",
	inactive_titlebar_bg = "#444444",
}

-- config.window_background_image = ""

config.window_decorations = "None"

config.window_padding = {
	left = 0,
	right = 0,
	top = 0,
	bottom = 0,
}

local act = wezterm.action

config.keys = {
	{ key = 'LeftArrow', mods = 'CTRL', action = act.ActivateTabRelative(-1) },
	{ key = 'RightArrow', mods = 'CTRL', action = act.ActivateTabRelative(1) },
	{ key = 'LeftArrow', mods = 'ALT', action = act.ActivateTabRelative(-1) },
	{ key = 'RightArrow', mods = 'ALT', action = act.ActivateTabRelative(1) },
	{
		key = 'K',
		mods = 'CTRL|SHIFT',
		action = act.Multiple {
			act.ClearScrollback 'ScrollbackAndViewport',
			act.SendKey { key = 'L', mods = 'CTRL' },
		},
	},
	{ key = 'LeftArrow', mods = 'CTRL', action = act.SendString '\x1b\x5b1;5D' },
	{ key = 'RightArrow', mods = 'CTRL', action = act.SendString '\x1b\x5b1;5C' },
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
config.enable_scroll_bar = true

for i = 1, 8 do
	-- ALT + number to activate that tab
	table.insert(config.keys, {
		key = tostring(i),
				 mods = 'ALT',
				 action = act.ActivateTab(i - 1),
	})
-- 	-- F1 through F8 to activate that tab
-- 	table.insert(config.keys, {
-- 		key = 'F' .. tostring(i),
-- 				 action = act.ActivateTab(i - 1),
-- 	})
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
function basename(s)
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
	
	return { { Text = tab.tab_index + 1 .. ': ' .. path .. '> ' .. process } }
end)
wezterm.on('format-window-title', function(tab, pane, tabs, panes, config)
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
	
	return path .. '> ' .. process
end)
-- Note to self
-- pane.current_working_dir returns an URL object
-- everything after # in URL's are ommitted, meaning file paths may be cut off

return config
