#!/bin/bash
## This script builds DEB package on a debian-based distribution
## Thanks to Saeed Rasooli <saeed.gnu@gmail.com>

pkgName=unity-scope-dilmaj
version=0.6

function getDirTotalSize(){
    du -ks "$1" | python2 -c "import sys;print(raw_input().split('\t')[0])"
}

if [ "$UID" != "0" ] ; then
  echo "Run this script as root"
  exit 1
fi

myPath="$0"
if [ "${myPath:0:2}" == "./" ] ; then
    myPath=$PWD${myPath:1}
elif [ "${myPath:0:1}" != "/" ] ; then
    myPath=$PWD/$myPath
fi

sourceDir="`dirname \"$myPath\"`"

tmpDir=/tmp/dilmaj-install-deb
mkdir -p "$tmpDir/DEBIAN"
mkdir -p "$tmpDir/usr/share/dbus-1/services"
mkdir -p "$tmpDir/usr/share/unity/scopes/info"
mkdir -p "$tmpDir/usr/share/unity-scopes/dilmaj"

cp -r "$sourceDir/data/icons" "$tmpDir/usr/share/icons"
cp "$sourceDir/data/dilmaj.scope" "$tmpDir/usr/share/unity/scopes/info/dilmaj.scope"
cp "$sourceDir/data/generic.db" "$tmpDir/usr/share/unity-scopes/dilmaj/generic.db"
cp "$sourceDir/data/unity-scope-dilmaj.service" "$tmpDir/usr/share/dbus-1/services/unity-scope-dilmaj.service"
cp "$sourceDir/src/unity_dilmaj_daemon.py" "$tmpDir/usr/share/unity-scopes/dilmaj/unity_dilmaj_daemon.py"
cp "$sourceDir/src/__init__.py" "$tmpDir/usr/share/unity-scopes/dilmaj/__init__.py"

chown -R root "$tmpDir"
installedSize=`getDirTotalSize "$tmpDir"`

depends=('python3')
depends+=('python3-gi')
depends+=('gir1.2-unity-5.0(>= 7)')
depends+=('gir1.2-dee-1.0(>= 1.2.5)')
depends+=('unity-scopes-runner')
depends+=('gir1.2-glib-2.0')

depends_str=$(printf ", %s" "${depends[@]}") ; depends_str=${depends_str:2}

echo "Package: $pkgName
Version: $version
Architecture: all
Maintainer: Ahmad Hamzeei <ahmadhamzeei@gmail.com>
Installed-Size: $installedSize
Depends: $depends_str
Section: Utilities
Priority: optional
Homepage: https://github.com/ahmadhamzeei
Description: Dilmaj scope for Unity
 Dilmaj is a small and fast English-to-Persian dictionary for Unity Dash.
" > "$tmpDir/DEBIAN/control"

pkgFile=${pkgName}_${version}-1_all.deb
dpkg-deb -b "$tmpDir" "$pkgFile"

rm -Rf "$tmpDir"

