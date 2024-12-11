// src/pages/Home.js
import React from 'react';
import { useQuery } from 'react-query';
import { Card, Row, Col, Button, Container } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { API } from '../constants';

const fetchAlbums = async () => {
  const res = await fetch(`${API}albums/`);
  const data = await res.json();
  return data;
};

const HomePage = () => {
  const { data, isLoading, isError } = useQuery('albums', fetchAlbums);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return <div>Error loading albums.</div>;
  }

  return (
    <Container>
      <h2>Album List</h2>
      <Row>
        {data.map((album) => {
          // Calculate the total playtime by summing all song lengths for the album
          const totalPlaytime = album.tracks.reduce(
            (total, track) => total + track.length,
            0
          );

          // Format the release date to show only the year
          const releaseYear = new Date(album.release_date).getFullYear();

          return (
            <Col key={album.id} sm={12} md={6} lg={4}>
              <Card className='mb-4'>
                <Card.Img
                  variant='top'
                  src={album.cover_image || '/static/covers/default.jpg'}
                />
                <Card.Body>
                  <Card.Title>{album.title}</Card.Title>
                  <Card.Subtitle className='mb-2 text-muted'>
                    {album.artist}
                  </Card.Subtitle>
                  <Card.Text>
                    <strong>Description: </strong>{album.description.substring(0, 100)}
                  </Card.Text>
                  <Card.Text>
                    <strong>Release Year:</strong> {releaseYear}
                  </Card.Text>
                  <Card.Text>
                    <strong>Total Playtime:</strong> {totalPlaytime} seconds
                  </Card.Text>
                  <Link to={`/albums/${album.id}`}>
                    <Button variant='primary'>View Details</Button>
                  </Link>
                </Card.Body>
              </Card>
            </Col>
          );
        })}
      </Row>
    </Container>
  );
};

export default HomePage;
