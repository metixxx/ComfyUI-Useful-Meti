<!-- metadata
title: "Useful-Meti: Timer, Image History & Save Nodes"
description: "Custom nodes for ComfyUI: workflow timer, image history gallery, and advanced image saver with path output"
tags: timer, image history, save image, generation time, past images, batch save, utility
-->

# 🔧 ComfyUI-Useful-Meti

A collection of practical custom nodes for ComfyUI by Meti.sh

---

## 📦 Nodes

| Node | Description |
| :--- | :--- |
| **⏱️ Generation Time** | Outputs the total execution time of your Nodes or workflow. |
| **📸 Past Images** | Keeps a history of your generated images (up to 10) and shows them in a live-updating grid. |
| **💾 Save Image Advanced** | Saves images with custom path and outputs filename & full path or Just Preview |

<div style="text-align: center;">
  <img src="images/Useful-Meti-01.png" style="max-width: 100%; height: auto; object-fit: contain; background-color: #f0f0f0;" />
</div>

> 📸 [View more examples](images/Useful-Meti-02.png)

---

## 🚀 Installation

1. Go to `ComfyUI/custom_nodes/`
2. Clone this repository:
   ```bash
   git clone https://github.com/metixxx/ComfyUI-Useful-Meti.git
   ```
3. Restart ComfyUI

> ✅ No extra dependencies needed. Works with ComfyUI's default environment.

---

## ⚙️ How to Use

### ⏱️ Generation Time

Place it anywhere in your workflow. Timer starts automatically.

| Inputs | Type | Description |
|--------|------|-------------|
| `input_any` | any | Data to pass through unchanged |
| `input_string` | STRING | Label for the time (default: "Generation") |

| Outputs | Type | Example |
|---------|------|---------|
| `passthrough` | any | Your original image/text |
| `time_with_label` | STRING | `"Generation: 2m 34s"` |
| `time_only` | STRING | `"(Runtime: 2m 34s)"` |

![GenerationTime](images/GenerationTime-example01.png)

Use this node to compare different models, samplers, or schedulers:

![GenerationTime](images/GenerationTime-example02.png)

> 📸 [View more examples](images/GenerationTime-example03.png)

---

### 📸 Past Images

Keeps a history of your generated images (up to 10) and shows them in a live-updating grid.  
The grid preserves each image's **original aspect ratio** inside the frame, so you can easily compare different outputs.

| Inputs | Type | Description |
|--------|------|-------------|
| `image` | IMAGE | Image batch to store |
| `preset` | INT | 2, 4, 6, 8, or 10 images |
| `image_name (opt)` | any | Optional image name |
| `image_path (opt)` | any | Optional file path |
| `reset_trigger` | BUTTON | Clears all history |

| Outputs | Type | Description |
|---------|------|-------------|
| `passthrough` | IMAGE | Pass-through the input image |
| `history_names` | STRING | List of image names |
| `history_paths` | STRING | List of full file paths |

![PastImages-01](images/PastImages-01.png)
![PastImages-02](images/PastImages-02.png) 

---

### 💾 Save Image Advanced

Save images with custom path and get filename + full path as output.

| Inputs | Type | Description |
|--------|------|-------------|
| `images` | IMAGE | Image(s) to save |
| `filename_prefix` | STRING | Prefix for the filename |
| `custom_path` | STRING | Custom save directory (leave empty for default ComfyUI output) |
| `mode` | `Save` / `Preview` | `Save` = writes to disk + shows preview, `Preview` = shows preview only |

| Outputs | Type | Description |
|---------|------|-------------|
| `image` | IMAGE | Pass-through the input image |
| `filename` | STRING | Name of the saved file |
| `full_path` | STRING | Full path of the saved file |

<table width="100%" style="max-width: 600px; margin: 0 auto;">
  <tr>
    <td align="center" width="50%">
      <img src="images/SaveImageAdvanced-01.png" width="220" style="border-radius: 6px;" />
      <br />
      <em>Save Mode</em>
    </td>
    <td align="center" width="50%">
      <img src="images/SaveImageAdvanced-02.png" width="220" style="border-radius: 6px;" />
      <br />
      <em>Preview Mode</em>
    </td>
  </tr>
</table>

---

## 🙏 Credits

- **Maintainer:** [Metixxx](https://github.com/metixxx)
- **Inspiration for Generation Time:** [Shannooty/ComfyUI-Timer-Nodes](https://github.com/Shannooty/ComfyUI-Timer-Nodes)

---

## 💰 Support

If you find this useful, you can send a donation via USDT:

| Network | Wallet Address |
|---------|----------------|
| **BEP20** | `0x7CBf0c5D7ECd5BAcD6BD13b3b2D4e8B3Ca9542AD` |
| **TRC20** | `TT1xEJMPNiBHtdA1pz4bCCxYgBajr1vtT1` |


<table width="100%" style="max-width: 500px; margin: 0 auto;">
  <tr>
    <td align="center" width="35%">
      <img src="images/qrcode-bep20.png" width="160" />
      <br />
      <strong>BEP20</strong>
    </td>
    <td align="center" width="30%">
      <!-- spacer -->
     </td>
    <td align="center" width="35%">
      <img src="images/qrcode-trc20.png" width="160" />
      <br />
      <strong>TRC20</strong>
     </td>
  </tr>
</table>


Thank you! 🙏

---

## ⚖️ License

GPL-3.0. See [LICENSE](LICENSE) file for details.

---

🔗 **GitHub:** [metixxx/ComfyUI-Useful-Meti](https://github.com/metixxx/ComfyUI-Useful-Meti)