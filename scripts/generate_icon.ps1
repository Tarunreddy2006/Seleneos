Add-Type -AssemblyName System.Drawing

function Generate-Icon([int]$size, [string]$outPath) {
    $bmp = New-Object System.Drawing.Bitmap($size, $size)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit

    # Transparent background
    $g.Clear([System.Drawing.Color]::Transparent)

    # Rounded squircle / circle background: Midnight indigo gradient
    $rect = New-Object System.Drawing.Rectangle(4, 4, ($size - 8), ($size - 8))
    $bgBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        (New-Object System.Drawing.Point(0, 0)),
        (New-Object System.Drawing.Point($size, $size)),
        [System.Drawing.Color]::FromArgb(255, 15, 23, 42),   # #0f172a
        [System.Drawing.Color]::FromArgb(255, 30, 58, 138)   # #1e3a8a
    )
    $g.FillEllipse($bgBrush, $rect)

    # Outer subtle luminous ring
    $borderPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(180, 56, 189, 248), [Math]::Max(2, [int]($size * 0.02)))
    $g.DrawEllipse($borderPen, $rect)

    # Golden celestial crescent (Selene)
    $crescentPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 245, 158, 11), [Math]::Max(3, [int]($size * 0.045)))
    $crescentRect = New-Object System.Drawing.Rectangle([int]($size * 0.15), [int]($size * 0.15), [int]($size * 0.7), [int]($size * 0.7))
    $g.DrawArc($crescentPen, $crescentRect, 45, 270)

    # Inner intelligence cyan orbital node
    $cyanPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 56, 189, 248), [Math]::Max(2, [int]($size * 0.035)))
    $cyanRect = New-Object System.Drawing.Rectangle([int]($size * 0.22), [int]($size * 0.22), [int]($size * 0.56), [int]($size * 0.56))
    $g.DrawArc($cyanPen, $cyanRect, -135, 220)

    # Stylized Serif / Modern 'S' for Seleneos
    $fontSize = [int]($size * 0.38)
    $font = New-Object System.Drawing.Font("Georgia", $fontSize, [System.Drawing.FontStyle]::Bold)
    $textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 255, 255, 255))
    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment = [System.Drawing.StringAlignment]::Center
    $sf.LineAlignment = [System.Drawing.StringAlignment]::Center

    # Slight glow shadow
    $shadowBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(100, 56, 189, 248))
    $g.DrawString("S", $font, $shadowBrush, [float]($size / 2) + 2, [float]($size / 2) - 1, $sf)
    $g.DrawString("S", $font, $textBrush, [float]($size / 2), [float]($size / 2) - 2, $sf)

    # Small golden star / intelligence beacon in top right
    $starX = [int]($size * 0.72)
    $starY = [int]($size * 0.25)
    $starR = [int]($size * 0.05)
    $starBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 251, 191, 36))
    $g.FillEllipse($starBrush, ($starX - $starR), ($starY - $starR), ($starR * 2), ($starR * 2))

    $dir = [System.IO.Path]::GetDirectoryName($outPath)
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    Write-Output "Generated: $outPath ($size x $size)"
}

$baseDir = "assets_icon"
Generate-Icon 192 "$baseDir\ic_launcher.png"
Generate-Icon 144 "$baseDir\mipmap-xxhdpi\ic_launcher.png"
Generate-Icon 96  "$baseDir\mipmap-xhdpi\ic_launcher.png"
Generate-Icon 72  "$baseDir\mipmap-hdpi\ic_launcher.png"
Generate-Icon 48  "$baseDir\mipmap-mdpi\ic_launcher.png"
