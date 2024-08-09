import { useEffect, useState, useRef } from "react";
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import { useParams } from "react-router-dom";
import "./ImageDisplay.css";
import LoadingGIF from "./assets/loading.gif";

const ImageDisplay = () => {
    const { uuid } = useParams<{ uuid: string }>();
    const [timeSpent, setTimeSpent] = useState(0);
    const [isLoading, setIsLoading] = useState(true);

    const imgRef = useRef({ downloadUrl: "", uuid: "", story: ""});

    function extractJsonContent(input: string): string {
        const endIndex = input.lastIndexOf('</JSON>');
        if (endIndex !== -1) {
          return input.substring(0, endIndex).trim();
        }
        return input;
      }

    const updateImg = (data) => {

        const story = extractJsonContent(data.story);
        console.log(story);
        imgRef.current = { downloadUrl: data.downloadUrl, uuid: data.uuid, story: "" };
    };

    useEffect(() => {

        let fetchUrl = setInterval(() => {

            fetch(`${process.env.REACT_APP_API_ENDPOINT}apis/images/${uuid}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => {
                if(!response.ok){
                    throw new Error('Not Generated yet');
                }
                return response.json()
            })
            .then(data => {
                updateImg(data);
                clearInterval(fetchUrl);
            })
            .catch((err) => console.log("err", err))

        }, 10000);

        return () => clearInterval(fetchUrl)
        
    }, []);

    useEffect(() => {
        let timer = setInterval(() => {
            setTimeSpent((val) => val + 1);
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        let checkImage = setInterval(() => {
            let image = new Image();
            image.src = imgRef.current.downloadUrl;
            image.onload = () => {
                setIsLoading(false);
                clearInterval(checkImage);
            };
            image.onerror = () => {
                setIsLoading(true);
            };
        }, 5000);

        return () => clearInterval(checkImage);
    }, []);

    return (
        <div className="box-group">
            <TransitionGroup style={{ display: 'flex' }}>
                <CSSTransition
                    key={imgRef.current.uuid}
                    timeout={5000}
                    classNames={"page-transition"}
                    unmountOnExit
                    in={true}
                >
                    {isLoading ? <LoadingComponent /> : <DisplayComponent url={imgRef.current.downloadUrl} />}
                </CSSTransition>
            </TransitionGroup>
        </div>
    );
};

const LoadingComponent = () => {
    return (
        <div className="bg-box">
            <img src={LoadingGIF} className="bg-image" alt="loading" />
        </div>
    )
};

const sampleText = {
    "ko": "18세기 조선의 궁녀였던 그녀는 왕실의 비밀을 알게 되었다. 음모에 휘말려 궁에서 쫓겨나 상인의 딸로 위장한 채 살아갔다. 그러나 그녀의 지혜와 용기로 결국 진실을 밝히고 정의를 되찾았다. 그녀의 이야기는 후대에 전설이 되어 전해졌고, 그녀의 용기는 많은 이들에게 희망이 되었다.",

    "en": "In 18th century Joseon, she was a court lady who discovered royal secrets. Entangled in a conspiracy, she was expelled from the palace and lived disguised as a merchant's daughter. However, with her wisdom and courage, she eventually uncovered the truth and restored justice. Her story became a legend passed down through generations, and her bravery inspired hope in many.",

    "ja": "18世紀の朝鮮で宮女だった彼女は、王室の秘密を知ってしまった。陰謀に巻き込まれ宮廷から追放され、商人の娘に扮して生きた。しかし、彼女の知恵と勇気で最終的に真実を明らかにし、正義を取り戻した。彼女の物語は後世に伝説として語り継がれ、彼女の勇気は多くの人々に希望を与えた。"
}

const DisplayComponent = ({ url }: { url: string }) => {
    return (
        <div className="bg-box">
            <div className="bg-textbox">
                <div className="bg-text">
                    <span>
                        {JSON.stringify(sampleText)}
                    </span>
                </div>
            </div>
            <img src={url} className="bg-image" alt="gallery" />
        </div>
    )
};

export default ImageDisplay;
