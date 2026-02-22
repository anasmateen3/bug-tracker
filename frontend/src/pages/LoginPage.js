import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Bug } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const success = await login(email, password);
    setLoading(false);
    if (success) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted/20 px-4">
      <div className="w-full max-w-md">
        <div className="bg-card rounded-lg border shadow-sm p-8">
          <div className="flex justify-center mb-6">
            <div className="flex items-center gap-2">
              <Bug className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold tracking-tight">BugTracker</span>
            </div>
          </div>
          
          <h2 className="text-2xl font-semibold tracking-tight mb-2 text-center">Welcome back</h2>
          <p className="text-sm text-muted-foreground text-center mb-6">Sign in to your account to continue</p>
          
          <form onSubmit={handleSubmit} className="space-y-4" data-testid="login-form">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                data-testid="login-email-input"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                data-testid="login-password-input"
              />
            </div>
            
            <Button type="submit" className="w-full" disabled={loading} data-testid="login-submit-btn">
              {loading ? 'Signing in...' : 'Sign in'}
            </Button>
          </form>
          
          <p className="text-sm text-center text-muted-foreground mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary hover:underline" data-testid="register-link">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
