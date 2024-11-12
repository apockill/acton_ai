# Steps I took to get this project up and running

## Failed: Install MyStudio

First, I confirmed the C650 was connected and working by installing 
myStudio.

```bash
wget https://github.com/elephantrobotics/myStudio/releases/download/v3.5.7/myStudio-3.5.7-arm64.AppImage
chmod a+x myStudio-3.5.7-arm64.AppImage
./myStudio-3.5.7-arm64.AppImage

```

## Connecting via USB

### 1. Find the tty path
```bash
ls /dev/ | grep ACM
```

### 2. Validate the Connection

```
validate_robot --port {your /dev/ttyACM# path}
```

This will likely fail the first time you run it. You can give permissions
by:

```bash
sudo chmod 666 {tty path}
```

If you get the following error, you need to set your robot to 'Transponder -> USB'
on the robots screen. 

```bash
TypeError: object of type 'NoneType' has no len()

```