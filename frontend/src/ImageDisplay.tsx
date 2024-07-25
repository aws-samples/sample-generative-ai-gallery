import { useEffect, useState, useRef } from "react";
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import { useParams } from "react-router-dom";
import "./ImageDisplay.css";
import LoadingGIF from "./assets/loading.gif";

const ImageDisplay = () => {
    const { uuid } = useParams<{ uuid: string }>();
    const [timeSpent, setTimeSpent] = useState(0);
    const [isLoading, setIsLoading] = useState(true);

    const imgRef = useRef({ downloadUrl: "", uuid: "" });

    const updateImg = (data) => {
        imgRef.current = { downloadUrl: data.downloadUrl, uuid: data.uuid };
    };

    useEffect(() => {
        try {
            fetch(`${process.env.REACT_APP_API_ENDPOINT}/apis/images/${uuid}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => response.json())
                .then(data => updateImg(data));
        } catch (err) {
            console.log(err);
        }
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
            <h3 style={{ color: "white" }}>Spent Time: {timeSpent}</h3>
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

const DisplayComponent = ({ url }: { url: string }) => {
    return (
        <div className="bg-box">
            <img src={url} className="bg-image" alt="gallery" />
        </div>
    )
};

export default ImageDisplay;
