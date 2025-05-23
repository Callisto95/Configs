# Custom URI Protocol Handler

A URI protocol handler is quite easy to create.

Create a `.desktop` file with:

```
Name=[any name]
Type=Application
MimeType=x-scheme-handler/[protocol];
Exec=[path to hander] [format]
NoDisplay=true # hide in application menus
```
The format is the following:

| Format | Result |
|---|---|
| %f | a single filename |
| %F | multiple filenames |
| %u | a single URL |
| %U | multiple URLs |
| %d | a single directory. Used in conjunction with %f to locate a file |
| %D | multiple directories. Used in conjunction with %F to locate files |
| %n | a single filename without a path |
| %N | multiple filenames without paths |
| %k | a URI or local filename of the location of the desktop file |
| %v | the name of the Device entry |

Then run `sudo update-desktop-database` or `update-desktop-database $HOME/.local/share/applications` and that's it.
