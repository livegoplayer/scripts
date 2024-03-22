$input_folder = "F:\mp4\11"
$output_folder = ""
$start_time = "00:00:26"
$end_time = "00:03:27"

# Check if input folder exists
if (!(Test-Path $input_folder -PathType Container)) {
    Write-Host "Error: Input folder '$input_folder' not found."
    Exit 1
}

# Prepare the command
$command = "& accelerate launch --num_cpu_threads_per_process=8 ./cut.py --input_folder=$input_folder"

if (![string]::IsNullOrEmpty($output_folder)) {
    $command += " --output_folder=$output_folder"
}

if (![string]::IsNullOrEmpty($start_time)) {
    if ($start_time -notmatch "\d{1,2}:\d{2}:\d{2}(\.\d{3})?") {
        Write-Host "Error: Invalid start_time format. Time format should be 'HH:MM:SS.MMM' or 'HH:MM:SS'."
        Exit 1
    }
    $command += " --start_time=$start_time"
}

if (![string]::IsNullOrEmpty($end_time)) {
    if ($end_time -notmatch "\d{1,2}:\d{2}:\d{2}") {
        Write-Host "Error: Invalid end_time format. Time format should be 'HH:MM:SS'."
        Exit 1
    }
    $command += " --end_time=$end_time"
}

# Check if both start_time and end_time are empty
if ([string]::IsNullOrEmpty($start_time) -and [string]::IsNullOrEmpty($end_time)) {
    Write-Host "Error: At least one of start_time or end_time must be provided."
    Exit 1
}

# Call the Python script with the constructed command
Invoke-Expression $command
