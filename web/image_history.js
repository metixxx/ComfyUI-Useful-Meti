import { app } from "../../../scripts/app.js";

const nodeImages = new Map();

function truncateTextToFit(text, maxWidth, ctx, fontSize) {
    // ابتدا فونت را تنظیم می‌کنیم
    ctx.font = `${fontSize}px Arial`;
    
    // اگر متن کامل جا می‌شود، همان را برگردان
    let width = ctx.measureText(text).width;
    if (width <= maxWidth) return text;
    
    // وگرنه با حذف حروف از آخر، متن را کوتاه کن
    let truncated = text;
    while (truncated.length > 3 && width > maxWidth) {
        truncated = truncated.slice(0, -1);
        width = ctx.measureText(truncated + "...").width;
    }
    return truncated + "...";
}

function getBestLayout(total) {
    if (total <= 1) return { cols: 1, rows: 1 };
    if (total <= 2) return { cols: 2, rows: 1 };
    if (total <= 4) return { cols: 2, rows: Math.ceil(total / 2) };
    if (total <= 6) return { cols: 3, rows: Math.ceil(total / 3) };
    if (total <= 8) return { cols: 4, rows: Math.ceil(total / 4) };
    if (total <= 10) return { cols: 5, rows: Math.ceil(total / 5) };
    return { cols: 5, rows: Math.ceil(total / 5) };
}

function drawImagesOnNode(node, ctx) {
    const data = nodeImages.get(node.id);
    if (!data || !data.images || data.images.length === 0) return;
    
    const resetWidget = node.widgets?.find(w => w.name === "🔴 RESET");
    let startY = 60;
    
    if (resetWidget && resetWidget.last_y) {
        startY = resetWidget.last_y + 35;
    }
    
    const frameSize = 180;
    const padding = 10;
    
    const total = data.images.length;
    const layout = getBestLayout(total);
    const cols = layout.cols;
    
    const cellW = (node.size[0] - padding * 2) / cols;
    const cellH = frameSize + 35;
    
    for (let i = 0; i < total; i++) {
        const img = data.images[i];
        if (!img.complete) continue;
        
        const col = i % cols;
        const row = Math.floor(i / cols);
        const x = padding + col * cellW;
        const y = startY + row * cellH;
        
        const imgRatio = img.width / img.height;
        const frameRatio = frameSize / frameSize;
        
        let drawW, drawH, imgX, imgY;
        
        if (imgRatio > frameRatio) {
            drawW = frameSize;
            drawH = frameSize / imgRatio;
            imgX = x + (frameSize - drawW) / 2;
            imgY = y + (frameSize - drawH) / 2;
        } else {
            drawH = frameSize;
            drawW = frameSize * imgRatio;
            imgX = x + (frameSize - drawW) / 2;
            imgY = y + (frameSize - drawH) / 2;
        }
        
        ctx.strokeStyle = "#555";
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, frameSize, frameSize);
        
        ctx.drawImage(img, imgX, imgY, drawW, drawH);
        
        ctx.fillStyle = "#FFFFFF";
        ctx.font = "bold 13px Arial";
        ctx.shadowBlur = 0;
        ctx.fillText(`#${total - i}`, x + 6, y + 22);
        
        let imageName = data.names[i];
        if (!imageName || imageName === "") {
            imageName = `Image_${total - i}`;
        }
        
        // حداکثر عرض مجاز برای نام (عرض فریم - 12 پیکسل)
        const maxNameWidth = frameSize - 12;
        const fontSize = 10;
        
        // محاسبه نام متناسب با عرض
        const shortName = truncateTextToFit(imageName, maxNameWidth, ctx, fontSize);
        
        ctx.fillStyle = "#CCCCCC";
        ctx.font = `${fontSize}px Arial`;
        ctx.fillText(shortName, x + 6, y + frameSize + 20);
    }
    
    const rows = layout.rows;
    const requiredWidth = padding * 2 + cols * (frameSize + 10);
    const requiredHeight = startY + rows * cellH + 20;
    
    if (node.size[0] !== requiredWidth || node.size[1] !== requiredHeight) {
        node.size = [requiredWidth, requiredHeight];
        node.setDirtyCanvas(true);
    }
}

app.registerExtension({
    name: "meti.image_history",
    
    getCustomWidgets(app) {
        return {
            RESET_TRIGGER(node, inputName, inputData) {
                let resetState = 0;
                const button = node.addWidget("button", "🔴 RESET", 0, () => {
                    resetState = 1;
                    button.value = 1;
                    button.name = "✅ RESET!";
                    
                    const presetWidget = node.widgets?.find(w => w.name === "preset");
                    if (presetWidget) {
                        presetWidget.value = "2 Images";
                    }
                    
                    setTimeout(() => {
                        resetState = 0;
                        button.value = 0;
                        button.name = "🔴 RESET";
                    }, 200);
                });
                button.serializeValue = () => resetState;
                return button;
            }
        };
    },
    
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "ImageHistoryBuffer") {
            
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(output) {
                onExecuted?.apply(this, arguments);
                
                const imagesInfo = output?.images_info;
                if (!imagesInfo || imagesInfo.length === 0) return;
                
                const images = [];
                const names = [];
                let loaded = 0;
                
                const reversedInfo = [...imagesInfo].reverse();
                
                reversedInfo.forEach((info, idx) => {
                    const img = new Image();
                    img.onload = () => {
                        loaded++;
                        if (loaded === reversedInfo.length) {
                            nodeImages.set(this.id, { images, names });
                            this.setDirtyCanvas(true);
                        }
                    };
                    img.onerror = () => {
                        loaded++;
                        if (loaded === reversedInfo.length) {
                            nodeImages.set(this.id, { images, names });
                            this.setDirtyCanvas(true);
                        }
                    };
                    img.src = `/view?filename=${encodeURIComponent(info.image_file)}&type=temp`;
                    images.push(img);
                    names.push(info.image_name || `Image_${info.index}`);
                });
            };
            
            const onDrawForeground = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function(ctx) {
                onDrawForeground?.apply(this, arguments);
                drawImagesOnNode(this, ctx);
            };
            
            const onResize = nodeType.prototype.onResize;
            nodeType.prototype.onResize = function() {
                onResize?.apply(this, arguments);
                this.setDirtyCanvas(true);
            };
        }
    }
});