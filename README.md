## 使用方式
### 说明
1. install-qinglong.sh 是兼容青龙训练脚本 + Akegarasu训练脚本 + https://github.com/bmaltais/kohya_ss 的兼容安装命令sh，需要梯子，不是必要的，如果你能很好的安装以上任一个脚本，忽略这个脚本，而且这个是linux版本，windows不适用
2. extract_lora_from_models.ps1 是解决webui supermerger 差分模型制作的一个示例脚本，使用之前需要你安装Akegarasu/lora-scripts的必备插件，即初始化venv
3. tagger.sh 和 tagger.py 是https://github.com/THUDM/CogVLM 这个项目的打标脚本，目前只有linux的 sh， python 文件通用, 主要是优化自然语言使其更接近标签， 比原版新增的功能：

   1).  去除不必要的词比如:"The image portrays"， 另外提供数组用来添加去除的内容
   
   2).  短语试用and连接， 三个单词以内短语的用逗号隔开的名词连接起来： 比如   orange， pink， and red,  => orange and pink and red, 另外提供一个名词数组用来添加常用名词，检索到这些名词之后就会自动连接。
   
   3).  去除所有句号，转逗号。
   
   4).  使用模型本身的功能把结果中的名词提取出来并且使用逗号连接，这个功能非常垃圾，并不能代替原来的打标软件，纯当个添头，因为这个语言模型本身就有问题，理解不了我给他的提示词。造成的结果是有时候能提取出来，有时候提取不出来，而且名词很多都没有提取出来。
   
   5).  支持子文件夹检索， 以后打标可以直接填根目录， 如果输出到不同的文件夹， 还会自动新建原来的分类文件夹。
   
