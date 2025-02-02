import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { apiClient, endpoints } from '../api/client';
import { toast } from 'react-hot-toast';

export default function LoginPage() {
  const [email, setEmail] = useState('admin@pmtool.test');
  const [password, setPassword] = useState('admin');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      formData.append('grant_type', 'password');

      const response = await apiClient.post(endpoints.login(), formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      localStorage.setItem('access_token', response.data.access_token);
      apiClient.defaults.headers.Authorization = `Bearer ${response.data.access_token}`;
      navigate('/');
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
