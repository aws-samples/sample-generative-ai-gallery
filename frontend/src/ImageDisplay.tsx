import { useEffect, useState, useRef } from "react";
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import { useParams } from "react-router-dom";
import "./ImageDisplay.css";
import LoadingGIF from "./assets/loading.gif";

interface StoryData {
    en: string;
    ko: string;
    ja: string;
}

const ImageDisplay = () => {
    const { uuid } = useParams<{ uuid: string }>();
    const [timeSpent, setTimeSpent] = useState(0);
    const [isLoading, setIsLoading] = useState(true);

    const imgRef = useRef<{ downloadUrl: string; uuid: string; story: StoryData }>({
        downloadUrl: "",
        uuid: "",
        story: { en: "", ko: "", ja: "" }
    });

    function extractJsonContent(input: string): string {
        const startIndex = input.indexOf('{');
        const endIndex = input.lastIndexOf('}');
        if (startIndex !== -1 && endIndex !== -1) {
            return input.substring(startIndex, endIndex + 1);
        }
        return input;
    }

    function parseStoryData(jsonString: string): StoryData {
        try {
            const parsedData = JSON.parse(jsonString);
            return {
                en: parsedData.en || "",
                ko: parsedData.ko || "",
                ja: parsedData.ja || ""
            };
        } catch (error) {
            console.error("Error parsing JSON:", error);
            return { en: "", ko: "", ja: "" };
        }
    }

    const updateImg = (data: { downloadUrl: string; uuid: string; story: string }) => {
        const jsonContent = extractJsonContent(data.story);
        const storyData = parseStoryData(jsonContent);
        imgRef.current = { downloadUrl: data.downloadUrl, uuid: data.uuid, story: storyData };
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
    }, [uuid]);

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
                    {isLoading ? <LoadingComponent /> : <DisplayComponent url={imgRef.current.downloadUrl} story={imgRef.current.story} />}
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

const DisplayComponent = ({ url, story }: { url: string, story: StoryData }) => {
    return (
        <div className="bg-box">
            <div className="bg-textbox">
                <div className="bg-text">
                    <span>
                        {story.en}<br /><br />
                        {story.ko}<br /><br />
                        {story.ja}
                    </span>
                </div>
            </div>
            <img src={url} className="bg-image" alt="gallery" />
        </div>
    )
};

export default ImageDisplay;