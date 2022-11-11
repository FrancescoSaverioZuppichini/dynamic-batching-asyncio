from typing import List

import torch
import torchvision.transforms as T
from PIL import Image
from torchvision.models import ResNet50_Weights, resnet50
from torchvision.transforms.functional import to_tensor


class Model:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = (
            resnet50(weights=ResNet50_Weights.IMAGENET1K_V1).eval().to(self.device)
        )
        self.transform = torch.nn.Sequential(
            T.Resize((224, 224)),
            T.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ).to(self.device)

    @torch.no_grad()
    def inference(self, images: List[Image.Image]) -> List[int]:
        # transform supports batching, let's create tensors first
        x = torch.stack([to_tensor(image) for image in images]).to(self.device)
        # transform them
        x = self.transform(x)
        logits = self.model(x)
        # no need for softmax, the biggest ones will always be the biggest ones
        preds = logits.argmax(1)
        return preds.cpu().tolist()


if __name__ == "__main__":
    # lazy test
    images = [Image.open("examples/cat.jpeg"), Image.open("examples/cat.jpeg")]
    print(Model().inference(images))
