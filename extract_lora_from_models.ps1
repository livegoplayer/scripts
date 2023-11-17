# LoRA svd_merge script by @bdsqlsz

$save_precision = "fp16" # precision in saving, default float | 保存精度, 可�? float、fp16、bf16, 默认 和源文件相同
$precision = "float" # precision in merging (float is recommended) | 合并时计算精�?, 可�? float、fp16、bf16, 推荐float
$dim = 128 # dim rank of output LoRA | dim rank等级, 默认 4
$model_tuned = "F:\BaiduNetdiskDownload\stable-diffusion-webui\models\Stable-diffusion\Anything-ink+smoke_v1.fp16.safetensors" # original LoRA model path need to resize, save as cpkt or safetensors | 需要合并的模型路径, 保存格式 cpkt �? safetensors，多个用空格隔开
$model_org = "F:\BaiduNetdiskDownload\stable-diffusion-webui\models\Stable-diffusion\Anything-ink.safetensors" # original LoRA model path need to resize, save as cpkt or safetensors | 需要合并的模型路径, 保存格式 cpkt �? safetensors，多个用空格隔开

# $ratios = "1.0 -1.0" # ratios for each model / LoRA模型合并比例，数量等于模型数量，多个用空格隔开
$save_to = "F:\BaiduNetdiskDownload\stable-diffusion-webui\models\Lora\smoke_ext.safetensors" # output LoRA model path, save as ckpt or safetensors | 输出路径, 保存格式 cpkt �? safetensors
$device = "cuda" # device to use, cuda for GPU | 使用 GPU�?, 默认 CPU
$conv_dim = 0 # Specify rank of output LoRA for Conv2d 3x3, None for same as new_rank | Conv2d 3x3输出，没有默认同new_rank

# Activate python venv
.\venv\Scripts\activate

$Env:HF_HOME = "huggingface"
$Env:XFORMERS_FORCE_DISABLE_TRITON = "1"
$ext_args = [System.Collections.ArrayList]::new()

# [void]$ext_args.Add("--models")
# foreach ($model in $models.Split(" ")) {
#     [void]$ext_args.Add($model)
# }

# [void]$ext_args.Add("--ratios")
# foreach ($ratio in $ratios.Split(" ")) {
#     [void]$ext_args.Add([float]$ratio)
# }

if ($conv_dim) {
  [void]$ext_args.Add("--conv_dim=" + $conv_dim)
}

# 制作差分lora
accelerate launch --num_cpu_threads_per_process=8 "./sd-scripts/networks/extract_lora_from_models.py" `
	--model_org=$model_org `
	--model_tuned=$model_tuned `
	--dim=$dim `
	--save_to=$save_to `
	--device=$device `
	--save_precision=$save_precision `
	$ext_args 


Write-Output "制作差分lora finished"
Read-Host | Out-Null ;