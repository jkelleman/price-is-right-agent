import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ItemDetail from './pages/ItemDetail';
import Alerts from './pages/Alerts';
import AddItem from './pages/AddItem';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/items/:id" element={<ItemDetail />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/add-item" element={<AddItem />} />
      </Routes>
    </Layout>
  );
}

export default App;
