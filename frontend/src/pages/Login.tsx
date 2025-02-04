import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { apiClient, endpoints } from '../api/client';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { setToken } = useAuth();
  const [email, setEmail] = useState('admin@pmtool.test');
  const [password, setPassword] = useState('pmtool');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    console.log('Attempting login with:', { email, password });

    try {
      console.log('Making API request to:', endpoints.login());
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      formData.append('grant_type', 'password');
      formData.append('scope', '');
      
      console.log('Making login request with OAuth2 password flow');
      const response = await apiClient.post(endpoints.login(), formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json'
        }
      });
      
      console.log('Login response:', response.data);
      
      if (!response.data.access_token) {
        throw new Error('No access token received');
      }
      
      console.log('Login successful, token:', response.data.access_token.slice(0, 10) + '...');
      setToken(response.data.access_token);
      navigate('/dashboard', { replace: true });
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);

    }
  };

  return (

    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <Card className="w-[400px]">
        <CardHeader>
          <CardTitle>Login to DocuPlanAI</CardTitle>
          <CardDescription>Enter your credentials to access your account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && (
              <div className="text-sm text-red-500">{error}</div>
            )}
            <div className="flex justify-between items-center">
              <a href="/reset-password" className="text-sm text-blue-600 hover:text-blue-800">
                Forgot Password?
              </a>
              <a href="/signup" className="text-sm text-blue-600 hover:text-blue-800">
                Create Account
              </a>
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Logging in...' : 'Login'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
