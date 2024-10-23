import os
import cv2
import argparse
import insightface
import onnxruntime
import numpy as np
from PIL import Image


def getFaceSwapModel(model_path: str):
    model = insightface.model_zoo.get_model(model_path)
    return model


def getFaceAnalyser(model_path: str, providers,
                    det_size=(320, 320)):
    face_analyser = insightface.app.FaceAnalysis(name="buffalo_l", root="./checkpoints", providers=providers)
    face_analyser.prepare(ctx_id=0, det_size=det_size)
    return face_analyser


def get_one_face(face_analyser,
                 frame:np.ndarray):
    face = face_analyser.get(frame)
    try:
        return face[0]
    except IndexError:
        return None

    
def get_many_faces(face_analyser,
                   frame:np.ndarray):
    """
    get faces from left to right by order
    """
    try:
        face = face_analyser.get(frame)
        return sorted(face, key=lambda x: x.bbox[0])
    except IndexError:
        return None


def swap_face(face_swapper,
              source_faces,
              target_faces,
              source_index,
              target_index,
              temp_frame):
    """
    paste source_face on target image
    """
    source_face = source_faces[source_index]
    target_face = target_faces[target_index]

    return face_swapper.get(temp_frame, target_face, source_face, paste_back=True)
 
    
def process(source_img: Image.Image,
            target_img: Image.Image,
            model: str):
    # load machine default available providers
    providers = onnxruntime.get_available_providers()

    # load face_analyser
    face_analyser = getFaceAnalyser(model, providers)
    
    # load face_swapper
    model_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), model)
    face_swapper = getFaceSwapModel(model_path)
    
    # read images
    source_img = cv2.cvtColor(np.array(source_img), cv2.COLOR_RGB2BGR)
    target_img = cv2.cvtColor(np.array(target_img), cv2.COLOR_RGB2BGR)
    
    # detect faces
    source_face = get_one_face(face_analyser, source_img)
    target_face = get_one_face(face_analyser, target_img)

    if source_face is None:
        raise Exception("No face found in the source image!")
    
    if target_face is None:
        raise Exception("No face found in the target image!")

    result = face_swapper.get(target_img, target_face, source_face, paste_back=True)
    
    result_image = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    return result_image


def parse_args():
    parser = argparse.ArgumentParser(description="Face swapping.")
    parser.add_argument("--source_img", type=str, required=True, help="Path to the source image.")
    parser.add_argument("--target_img", type=str, required=True, help="Path to the target image.")
    parser.add_argument("--output_img", type=str, required=False, default="result.png", help="Path and filename for the output image.")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    
    args = parse_args()
    
    source_img = Image.open(args.source_img)
    target_img = Image.open(args.target_img)

    # Download from https://huggingface.co/deepinsight/inswapper/tree/main
    model = "./checkpoints/inswapper_128.onnx"
    result_image = process(source_img, target_img, model)
    
    # Save the result
    result_image.save(args.output_img)
    print(f'Result successfully saved: {args.output_img}')
