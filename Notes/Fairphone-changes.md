# Changes I made to my Fairphone 6

## disable gesture 'go back'

```shell
adb shell settings put secure back_gesture_inset_scale_left 0
```

> [!Note]
> This is because I use a third party app to add it back (and more).
> If I don't disable it, I go back twice for every back.
