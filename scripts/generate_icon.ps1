Add-Type -AssemblyName System.Drawing

$logoSource = Resolve-Path "app_logo.jpeg" -ErrorAction SilentlyContinue
if (-not $logoSource -or -not (Test-Path $logoSource)) {
    Write-Error "app_logo.jpeg not found in project directory!"
    exit 1
}

$srcImg = [System.Drawing.Image]::FromFile($logoSource)

function Resize-Logo([int]$size, [string]$outPath) {
    $bmp = New-Object System.Drawing.Bitmap($size, $size)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

    $g.Clear([System.Drawing.Color]::Transparent)

    # Draw image scaled to fit size x size
    $g.DrawImage($srcImg, 0, 0, $size, $size)

    $dir = [System.IO.Path]::GetDirectoryName($outPath)
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    Write-Output "Generated from app_logo.jpeg: $outPath ($size x $size)"
}

$baseDir = "assets_icon"
Resize-Logo 192 "$baseDir\ic_launcher.png"
Resize-Logo 144 "$baseDir\mipmap-xxhdpi\ic_launcher.png"
Resize-Logo 96  "$baseDir\mipmap-xhdpi\ic_launcher.png"
Resize-Logo 72  "$baseDir\mipmap-hdpi\ic_launcher.png"
Resize-Logo 48  "$baseDir\mipmap-mdpi\ic_launcher.png"

$srcImg.Dispose()
