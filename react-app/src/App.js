// src/App.js
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/Home';
import AlbumPage from './pages/Album';
import { Container } from 'react-bootstrap';

function App() {
  return (
    <Router>
      <Container>
        <Routes>
          <Route path='/' element={<HomePage />} />
          <Route path='/albums/:id' element={<AlbumPage />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
