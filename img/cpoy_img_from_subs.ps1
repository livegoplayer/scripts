$sourcePath = "F:\mp4"
$targetPath = ""

# Check if the source directory exists
if (-not (Test-Path -Path $sourcePath)) {
    Write-Host "Source directory does not exist"
    exit
}

# If target directory is not specified or is empty, set it to the source directory
if (-not $targetPath -or $targetPath -eq "") {
    $targetPath = $sourcePath
}

# Ensure the target directory exists, including any necessary parent directories
$targetFullPath = (Resolve-Path -Path $targetPath).Path
if (-not (Test-Path -Path $targetFullPath)) {
    try {
        New-Item -ItemType Directory -Path $targetFullPath -Force | Out-Null
    } catch {
        Write-Host "Failed to create target directory: $_" -ForegroundColor Red
        exit
    }
}

# Create a subdirectory named 'imgcopy' under the target directory
$targetImgCopyPath = Join-Path -Path $targetFullPath -ChildPath "imgcopy"
if (-not $targetImgCopyPath) {
    Write-Host "Failed to create target 'imgcopy' directory" -ForegroundColor Red
    exit
}
New-Item -ItemType Directory -Path $targetImgCopyPath -Force | Out-Null

# Supported image formats
$supportedFormats = @("*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tif", "*.tiff", "*.ico", "*.svg", "*.webp")

# Recursively get all supported image files in the source directory
$imageFiles = Get-ChildItem -Path $sourcePath -Include $supportedFormats -File -Recurse

# Sort files by name
$imageFiles = $imageFiles | Sort-Object Name

# Copy and rename image files
for ($i = 0; $i -lt $imageFiles.Count; $i++) {
    $newFileName = "{0:D4}{1}" -f ($i + 1), (Get-Item $imageFiles[$i].FullName).Extension
    $destinationPath = Join-Path -Path $targetImgCopyPath -ChildPath $newFileName
    try {
        Copy-Item -Path $imageFiles[$i].FullName -Destination $destinationPath -ErrorAction Stop
        Write-Host ("Copying file: " + $imageFiles[$i].FullName + " to " + $destinationPath) -ForegroundColor Green
    } catch {
        Write-Host ("Failed to copy file: " + $imageFiles[$i].FullName + " to " + $destinationPath) -ForegroundColor Red
        Write-Host ("Error: $_") -ForegroundColor Red
    }
}
