import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Map.css';

// Import marker icons
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix marker icon issues
import L from 'leaflet';
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

interface Airport {
  id: number;
  name: string;
  iata_code: string;
  city: string;
  country: string;
  latitude: number;
  longitude: number;
}

interface Flight {
  id: number;
  flight_number: string;
  airline: number;
  departure_airport: number;
  arrival_airport: number;
  scheduled_departure: string;
  scheduled_arrival: string;
}

interface Airline {
  id: number;
  name: string;
  iata_code: string;
}

// Add this utility function
const formatTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

const Map: React.FC = () => {
  const navigate = useNavigate();
  const [airports, setAirports] = useState<Airport[]>([]);
  const [flights, setFlights] = useState<Flight[]>([]);
  const [airlines, setAirlines] = useState<Record<number, Airline>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [availableDates, setAvailableDates] = useState<string[]>([]);

  const center: LatLngExpression = [46.2276, 2.2137]; // Center of France

  // Add this function to filter flights by date
  const getFilteredFlights = () => {
    return flights.filter(flight => {
      const flightDate = new Date(flight.scheduled_departure).toISOString().split('T')[0];
      return flightDate === selectedDate;
    });
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchData = async () => {
      try {
        const [airportsRes, flightsRes, airlinesRes, datesRes] = await Promise.all([
          axios.get('http://localhost:8000/api/airports/', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get('http://localhost:8000/api/flights/', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get('http://localhost:8000/api/airlines/', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get('http://localhost:8000/api/turnarounds/available_dates/', {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);

        const airlineMap = airlinesRes.data.reduce((acc: Record<number, Airline>, airline: Airline) => {
          acc[airline.id] = airline;
          return acc;
        }, {});

        setAirports(airportsRes.data);
        setFlights(flightsRes.data);
        setAirlines(airlineMap);
        setAvailableDates(datesRes.data);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  const getFlightPath = (flight: Flight): LatLngExpression[] => {
    const depAirport = airports.find(a => a.id === flight.departure_airport);
    const arrAirport = airports.find(a => a.id === flight.arrival_airport);

    if (!depAirport || !arrAirport) return [];

    return [
      [depAirport.latitude, depAirport.longitude],
      [arrAirport.latitude, arrAirport.longitude]
    ];
  };

  // Add this function to calculate the midpoint for the flight time label
  const getFlightMidpoint = (path: LatLngExpression[]): LatLngExpression => {
    const [start, end] = path;
    const [lat1, lon1] = start as number[];
    const [lat2, lon2] = end as number[];
    return [(lat1 + lat2) / 2, (lon1 + lon2) / 2];
  };

  if (loading) return <div className="loading">Loading map...</div>;
  if (error) return <div className="error">{error}</div>;

  const defaultCenter: LatLngExpression = [46.2276, 2.2137];

  return (
    <div className="map-page">
      <header className="map-header">
        <h1>Flight Map</h1>
        <div className="map-controls">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            min={availableDates[0]}
            max={availableDates[availableDates.length - 1]}
            className={availableDates.includes(selectedDate) ? 'date-available' : 'date-unavailable'}
          />
          <button onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
        </div>
      </header>
      <div className="map-container">
        <MapContainer 
          key="map"
          center={defaultCenter} 
          zoom={6} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {airports.map(airport => (
            <Marker
              key={airport.id}
              position={[airport.latitude, airport.longitude]}
            >
              <Popup>
                <strong>{airport.name}</strong>
                <br />
                {airport.iata_code} - {airport.city}
                <br />
                {airport.country}
              </Popup>
            </Marker>
          ))}
          {getFilteredFlights().map(flight => {
            const airline = airlines[flight.airline];
            const path = getFlightPath(flight);
            if (path.length === 0 || !airline) return null;

            const midpoint = getFlightMidpoint(path);
            const departureTime = formatTime(flight.scheduled_departure);
            const arrivalTime = formatTime(flight.scheduled_arrival);

            return (
              <React.Fragment key={flight.id}>
                <Polyline
                  positions={path}
                  color="#3498db"
                  weight={4}
                  opacity={0.6}
                  pathOptions={{
                    className: 'flight-path'
                  }}
                >
                  <Popup>
                    <strong>{airline.name} {airline.iata_code}{flight.flight_number}</strong>
                    <br />
                    Departure: {new Date(flight.scheduled_departure).toLocaleString()}
                    <br />
                    Arrival: {new Date(flight.scheduled_arrival).toLocaleString()}
                  </Popup>
                </Polyline>
                <Popup
                  position={midpoint}
                  closeButton={false}
                  closeOnClick={false}
                  autoPan={false}
                  className="flight-time-label"
                >
                  <div className="flight-time">
                    {departureTime} → {arrivalTime}
                  </div>
                </Popup>
              </React.Fragment>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
};

export default Map; 