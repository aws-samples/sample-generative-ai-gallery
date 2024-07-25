import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import PhotoStart from './PhotoStart';
import PhotoTake from './PhotoTake';
import ImageDisplay from './ImageDisplay';
import { QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import '@aws-amplify/ui-react/styles.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
    },
  },
  queryCache: new QueryCache({
    onError: (error) => {
      console.error(error);
    },
  }),
});

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            <Route path="/" element={<Navigate to="/photo/start" replace />} />
            <Route path="/photo/start" element={<PhotoStart />} />
            <Route path="/photo/take" element={<PhotoTake />} />
            <Route path="/image/:uuid" element={<ImageDisplay />}/>
          </Routes>
        </Router>
    </QueryClientProvider>

  );
};

export default App;
