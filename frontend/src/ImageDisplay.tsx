import { useEffect, useState } from "react";
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import { useQuery } from '@tanstack/react-query'
import { useParams } from "react-router-dom";
import "./ImageDisplay.css";


const ImageDisplay = () => {

    const [img, setImg] = useState({downloadUrl: Date.now().toString(), uuid: ""});
    const { uuid } = useParams<{ uuid: string }>();
    const [ curTime, setCurTime ] = useState<number>(Date.now());
    const [ timeSpent, setTimeSpent ] = useState(0);
    
    const callApi = async () => {
        try{
            const response = await fetch(`${process.env.REACT_APP_API_ENDPOINT}/apis/images/${uuid}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            return await response.json();
        } catch (err) {
            console.log(err);
        }
    }

    const { data } = useQuery({
        queryKey: ['display'], 
        queryFn: callApi,
        refetchInterval: 5000,
        refetchIntervalInBackground: true,
    });

    useEffect(() => {
        if(data && data.uuid){
              setImg(data);
        }
    }, [data]);
    
    useEffect(() => {
        let timer = setInterval(() => {
            setTimeSpent((val) => val+1);
        }, 1000);

        return () => clearInterval(timer)
      }, []);

    if (img.downloadUrl === "") 
      return (
        <div className="loading-view">
                <div className="spinner" />
        </div>
      );
  
    return (
        <div className="box-group">
          <h3 style={{color:"white"}}>Spent Time: {timeSpent}</h3>
          <TransitionGroup style={{ display: 'flex'}}>
              {
                <CSSTransition
                    key={img.uuid}
                    timeout={5000}
                    classNames={"page-transition"}
                    unmountOnExit
                    in={true}
                >
                  <DisplayComponent url={img.downloadUrl} />
                </CSSTransition>
              }
          </TransitionGroup>    
        </div>
    );
}

const DisplayComponent = ({url}: {url:string}) => {

    return (
        <div className="bg-box"> 
            <img src={url} className="bg-image" alt="gallery" />
        </div>
    )
}

  
export default ImageDisplay;
