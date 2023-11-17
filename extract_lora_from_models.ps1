$save_precision = "fp16" # precision in saving, default float | float p16 f16
$precision = "float" # precision in merging (float is recommended) | float | p16 | f16
$dim = 128 # dim rank of output LoRA 
$model_tuned = "F:\BaiduNetdiskDownload\stable-diffusion-webui\models\Stable-diffusion\Anything-ink+smoke_v1.fp16.safetensors" # a x 1
$model_org = "F:\BaiduNetdiskDownload\stable-diffusion-webui\models\Stable-diffusion\Anything-ink.safetensors" # b x 1

$save_to = "F:\BaiduNetdiskDownload\stable-diffusion-webui\models\Lora\smoke_ext.safetensors" # output LoRA model path, save as ckpt or safetensors
$device = "cuda" # device to use, cuda for GPU 
$conv_dim = 0 # Specify rank of output LoRA for Conv2d 3x3, None for same as new_rank 

# Activate python venv
.\venv\Scripts\activate

$Env:HF_HOME = "huggingface"
$Env:XFORMERS_FORCE_DISABLE_TRITON = "1"
$ext_args = [System.Collections.ArrayList]::new()

if ($conv_dim) {
  [void]$ext_args.Add("--conv_dim=" + $conv_dim)
}

accelerate launch --num_cpu_threads_per_process=8 "./sd-scripts/networks/extract_lora_from_models.py" `
	--model_org=$model_org `
	--model_tuned=$model_tuned `
	--dim=$dim `
	--save_to=$save_to `
	--device=$device `
	--save_precision=$save_precision `
	$ext_args 


Write-Output "extract lora finished"
Read-Host | Out-Null ;