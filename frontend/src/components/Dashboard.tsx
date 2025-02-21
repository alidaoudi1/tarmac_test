import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Dashboard.css';

interface Airline {
  id: number;
  name: string;
  iata_code: string;
}

interface Airport {
  id: number;
  name: string;
  iata_code: string;
  city: string;
  country: string;
}

interface Flight {
  id: number;
  flight_number: string;
  airline: number;
  departure_airport: number;
  arrival_airport: number;
  scheduled_departure: string;
  scheduled_arrival: string;
  actual_departure: string | null;
  actual_arrival: string | null;
}

interface Turnaround {
  id: number;
  arrival_flight: number;
  departure_flight: number;
  airport: number;
  scheduled_start: string;
  actual_start: string | null;
  scheduled_end: string;
  actual_end: string | null;
}

interface AirlineTurnaroundStats {
  airline: string;
  average_duration: number;
}

interface DateAirportFilter {
  date: string;
  airport_code: string;
  availableDates: string[];
}

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [flights, setFlights] = useState<Flight[]>([]);
  const [turnarounds, setTurnarounds] = useState<Turnaround[]>([]);
  const [airlines, setAirlines] = useState<Record<number, Airline>>({});
  const [airports, setAirports] = useState<Record<number, Airport>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [airlineStats, setAirlineStats] = useState<AirlineTurnaroundStats[]>([]);
  const [dateFilter, setDateFilter] = useState<DateAirportFilter>({
    date: new Date().toISOString().split('T')[0],
    airport_code: '',
    availableDates: []
  });
  const [filteredTurnarounds, setFilteredTurnarounds] = useState<Turnaround[]>([]);
  const [availableAirports, setAvailableAirports] = useState<Airport[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchData = async () => {
      try {
        const [flightsResponse, turnaroundsResponse, airlinesResponse, airportsResponse, statsResponse, datesResponse] = await Promise.all([
          axios.get('http://localhost:8000/api/flights/', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get('http://localhost:8000/api/turnarounds/', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get('http://localhost:8000/api/airlines/', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get('http://localhost:8000/api/airports/', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get('http://localhost:8000/api/airlines/turnaround_stats/', {
            headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get('http://localhost:8000/api/turnarounds/available_dates/', {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);

        // Create lookup objects
        const airlineMap = airlinesResponse.data.reduce((acc: Record<number, Airline>, airline: Airline) => {
          acc[airline.id] = airline;
          return acc;
        }, {});
        
        const airportMap = airportsResponse.data.reduce((acc: Record<number, Airport>, airport: Airport) => {
          acc[airport.id] = airport;
          return acc;
        }, {});

        setAirlines(airlineMap);
        setAirports(airportMap);
        setFlights(flightsResponse.data);
        setTurnarounds(turnaroundsResponse.data);
        setAirlineStats(statsResponse.data);
        setDateFilter(prev => ({ ...prev, availableDates: datesResponse.data }));
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to fetch data');
        if (err.response?.status === 401) {
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  const calculateTurnaroundTime = (turnaround: Turnaround): string => {
    const start = new Date(turnaround.scheduled_start);
    const end = new Date(turnaround.scheduled_end);
    const diffHours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
    return formatDuration(diffHours);
  };

  const formatDuration = (hours: number): string => {
    const h = Math.floor(hours);
    const minutes = Math.round((hours - h) * 60);
    return `${h}h ${minutes}m`;
  };

  const getAirline = (id: number): Airline | undefined => airlines[id];
  const getAirport = (id: number): Airport | undefined => airports[id];

  const handleFilterSubmit = async () => {
    if (!dateFilter.date || !dateFilter.airport_code) {
      setError('Both date and airport are required');
      return;
    }

    try {
      const response = await axios.get(
        `http://localhost:8000/api/turnarounds/by_date_and_airport/`,
        {
          params: {
            date: dateFilter.date,
            airport_code: dateFilter.airport_code
          },
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        }
      );
      setFilteredTurnarounds(response.data);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to fetch filtered data');
      setFilteredTurnarounds([]);
    }
  };

  const isDateAvailable = (date: string): boolean => {
    return dateFilter.availableDates.includes(date);
  };

  const fetchAvailableAirports = async (date: string) => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/airports/available_airports/`,
        {
          params: { date },
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        }
      );
      setAvailableAirports(response.data);
    } catch (err) {
      console.error('Failed to fetch available airports:', err);
    }
  };

  const handleDateChange = (date: string) => {
    setError('');
    setFilteredTurnarounds([]);
    setDateFilter({ ...dateFilter, date, airport_code: '' });
    fetchAvailableAirports(date);
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Flight Dashboard</h1>
        <div className="header-buttons">
          <button onClick={() => navigate('/map')} className="map-button">View Map</button>
          <button onClick={() => {
            localStorage.removeItem('token');
            navigate('/login');
          }}>Logout</button>
        </div>
      </header>

      <section className="filter-section">
        <h2>Filter Turnarounds</h2>
        {error && <div className="error-message">{error}</div>}
        <div className="filter-form">
          <div className="form-group">
            <label htmlFor="date">Date *</label>
            <input
              type="date"
              id="date"
              value={dateFilter.date}
              onChange={(e) => handleDateChange(e.target.value)}
              className={isDateAvailable(dateFilter.date) ? 'date-available' : 'date-unavailable'}
              min={dateFilter.availableDates[0]}
              max={dateFilter.availableDates[dateFilter.availableDates.length - 1]}
              required
            />
            {!isDateAvailable(dateFilter.date) && (
              <span className="date-warning">No flights on this date</span>
            )}
          </div>
          <div className="form-group">
            <label htmlFor="airport">Airport *</label>
            <select
              id="airport"
              value={dateFilter.airport_code}
              onChange={(e) => {
                setError('');
                setFilteredTurnarounds([]);
                setDateFilter({ ...dateFilter, airport_code: e.target.value });
              }}
              required
              disabled={availableAirports.length === 0}
            >
              <option value="">Select Airport</option>
              {availableAirports.map(airport => (
                <option key={airport.id} value={airport.iata_code}>
                  {airport.iata_code} - {airport.name} ({airport.city})
                </option>
              ))}
            </select>
            {availableAirports.length === 0 && dateFilter.date && (
              <span className="date-warning">No airports available for this date</span>
            )}
          </div>
          <button 
            onClick={handleFilterSubmit}
            disabled={!dateFilter.date || !dateFilter.airport_code}
          >
            Filter
          </button>
        </div>
        {filteredTurnarounds.length > 0 && (
          <div className="filtered-results">
            <h3>Filtered Turnarounds</h3>
            <div className="turnarounds-table">
              <table>
                <thead>
                  <tr>
                    <th>Airport</th>
                    <th>Arrival Flight</th>
                    <th>Departure Flight</th>
                    <th>Scheduled Duration</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTurnarounds.map((turnaround) => {
                    const airport = getAirport(turnaround.airport);
                    const arrFlight = flights.find(f => f.id === turnaround.arrival_flight);
                    const depFlight = flights.find(f => f.id === turnaround.departure_flight);
                    const arrAirline = arrFlight ? getAirline(arrFlight.airline) : undefined;
                    const depAirline = depFlight ? getAirline(depFlight.airline) : undefined;

                    if (!airport || !arrFlight || !depFlight || !arrAirline || !depAirline) return null;

                    return (
                      <tr key={turnaround.id}>
                        <td>{`${airport.iata_code} (${airport.city})`}</td>
                        <td>{`${arrAirline.iata_code}${arrFlight.flight_number}`}</td>
                        <td>{`${depAirline.iata_code}${depFlight.flight_number}`}</td>
                        <td>{calculateTurnaroundTime(turnaround)}</td>
                        <td className={turnaround.actual_start ? 'active' : 'scheduled'}>
                          {turnaround.actual_start ? 'In Progress' : 'Scheduled'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      <section className="airline-stats-section">
        <h2>Airline Turnaround Statistics</h2>
        <div className="stats-table">
          <table>
            <thead>
              <tr>
                <th>Airline</th>
                <th>Average Turnaround Duration</th>
              </tr>
            </thead>
            <tbody>
              {airlineStats.map((stat, index) => (
                <tr key={index}>
                  <td>{stat.airline}</td>
                  <td>{formatDuration(stat.average_duration)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="flights-section">
        <h2>Active Flights</h2>
        <div className="flights-table">
          <table>
            <thead>
              <tr>
                <th>Flight</th>
                <th>Airline</th>
                <th>From</th>
                <th>To</th>
                <th>Scheduled Departure</th>
                <th>Scheduled Arrival</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {flights.map((flight) => {
                const airline = getAirline(flight.airline);
                const depAirport = getAirport(flight.departure_airport);
                const arrAirport = getAirport(flight.arrival_airport);
                
                if (!airline || !depAirport || !arrAirport) return null;

                return (
                  <tr key={flight.id}>
                    <td>{airline.iata_code}{flight.flight_number}</td>
                    <td>{airline.name}</td>
                    <td>{`${depAirport.iata_code} (${depAirport.city})`}</td>
                    <td>{`${arrAirport.iata_code} (${arrAirport.city})`}</td>
                    <td>{new Date(flight.scheduled_departure).toLocaleString()}</td>
                    <td>{new Date(flight.scheduled_arrival).toLocaleString()}</td>
                    <td className={flight.actual_departure ? 'active' : 'scheduled'}>
                      {flight.actual_departure ? 'Active' : 'Scheduled'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="turnarounds-section">
        <h2>Turnarounds</h2>
        <div className="turnarounds-table">
          <table>
            <thead>
              <tr>
                <th>Airport</th>
                <th>Arrival Flight</th>
                <th>Departure Flight</th>
                <th>Scheduled Duration</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {turnarounds.map((turnaround) => {
                const airport = getAirport(turnaround.airport);
                const arrFlight = flights.find(f => f.id === turnaround.arrival_flight);
                const depFlight = flights.find(f => f.id === turnaround.departure_flight);
                const arrAirline = arrFlight ? getAirline(arrFlight.airline) : undefined;
                const depAirline = depFlight ? getAirline(depFlight.airline) : undefined;

                if (!airport || !arrFlight || !depFlight || !arrAirline || !depAirline) return null;

                return (
                  <tr key={turnaround.id}>
                    <td>{`${airport.iata_code} (${airport.city})`}</td>
                    <td>{`${arrAirline.iata_code}${arrFlight.flight_number}`}</td>
                    <td>{`${depAirline.iata_code}${depFlight.flight_number}`}</td>
                    <td>{calculateTurnaroundTime(turnaround)}</td>
                    <td className={turnaround.actual_start ? 'active' : 'scheduled'}>
                      {turnaround.actual_start ? 'In Progress' : 'Scheduled'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}; 