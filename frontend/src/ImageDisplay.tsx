import React, { useEffect, useState, useRef } from "react";
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import { useParams } from "react-router-dom";
import "./ImageDisplay.css";
import LoadingGIF from "./assets/loading.gif";

const ImageDisplay = () => {
    const { uuid } = useParams();
    const [timeSpent, setTimeSpent] = useState(0);
    const [isLoading, setIsLoading] = useState(true);

    const imgRef = useRef({ downloadUrl: "", uuid: "", story: {} });

    function extractJsonContent(input) {
        const endIndex = input.lastIndexOf('</JSON>');
        if (endIndex !== -1) {
          return input.substring(0, endIndex).trim();
        }
        return input;
    }

    const updateImg = (data) => {
        const storyJson = JSON.parse(extractJsonContent(data.story));
        imgRef.current = { downloadUrl: data.downloadUrl, uuid: data.uuid, story: storyJson };
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
                    classNames="page-transition"
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

const DisplayComponent = ({ url, story }) => {
    const formattedStory = Object.values(story).join('\n\n\n');

    return (
        <div className="bg-box">
            <div className="bg-textbox">
                <div className="bg-text">
                    <pre>{formattedStory}</pre>
                </div>
            </div>
            <img src={url} className="bg-image" alt="gallery" />
        </div>
    )
};

export default ImageDisplay;