local wezterm = require 'wezterm'
local config = {}

config.font = wezterm.font "Fira Code Retina"

config.colors = {
	foreground = "#FFFFFF",
	background = "#222222",
	cursor_bg = "#FFFFFF",
-- 	selection_fg = "#FFFFFF",
	selection_bg = "#360e00",
	tab_bar = {
		inactive_tab_edge = "#000000",
-- 		background = "#FF4500"
		active_tab = {
			bg_color = "#222222",
			fg_color = "#FF4500"
		},
		inactive_tab = {
			bg_color = "#000000",
			fg_color = "#FFFFFF"
		},
		inactive_tab_hover = {
			bg_color = "#222222",
			fg_color = "#FFFFFF"
		},
		new_tab = {
			bg_color = "#000000",
			fg_color = "#FF4500"
		},
		new_tab_hover = {
			bg_color = "#000000",
			fg_color = "#FFFFFF"
		}
	}
}

config.window_frame = {
	font = wezterm.font "Fira Code Retina",
	active_titlebar_bg = "#000000",
}

-- config.window_background_image = ""

-- both together are the smoothest transition
local mux = wezterm.mux
wezterm.on("gui-startup", function()
	local _, _, window = mux.spawn_window{}
	window:gui_window():maximize()
end)

config.initial_cols = 190
config.initial_rows = 50

config.window_decorations = "None"

return config
