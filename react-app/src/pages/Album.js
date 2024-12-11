// src/pages/Album.js
import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { Card, Button, Container, Breadcrumb } from 'react-bootstrap';
import { API } from '../constants';

const fetchAlbum = async (id) => {
  const res = await fetch(`${API}albums/${id}/`);
  const data = await res.json();
  return data;
};

const AlbumPage = () => {
  const { id } = useParams();
  const { data, isLoading, isError } = useQuery(['album', id], () =>
    fetchAlbum(id)
  );

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return <div>Error loading album details.</div>;
  }

  const totalPlaytime = data.tracks.reduce(
    (total, track) => total + track.length,
    0
  ); // Sum all song lengths for total playtime

  const releaseYear = new Date(data.release_date).getFullYear();

  return (
    <Container>
      <Breadcrumb>
        <Breadcrumb.Item>
          <Link to='/'>Home</Link>
        </Breadcrumb.Item>
        <Breadcrumb.Item active>Album Details</Breadcrumb.Item>
      </Breadcrumb>

      <h2>{data.title}</h2>
      <Card>
        {/* Resize the image to be responsive */}
        <Card.Img
          variant='top'
          src={data.cover_image || '/static/covers/default.jpg'}
          style={{ width: '100%', maxHeight: '400px', objectFit: 'cover' }}
        />
        <Card.Body>
          <Card.Title>{data.artist}</Card.Title>
          <Card.Text><strong>Description:</strong>{data.description}</Card.Text>
          <Card.Text>
            <strong>Release Year:</strong> {releaseYear}
          </Card.Text>
          <Card.Text>
            <strong>Total Playtime:</strong> {totalPlaytime} seconds
          </Card.Text>
          <Link to='/'>
            <Button variant='secondary'>Back to Home</Button>
          </Link>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default AlbumPage;
