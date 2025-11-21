
type AuthEvent = 'accessChanged' | 'refreshChanged' | 'loggedOut';

type Listener = (event: AuthEvent) => void;

class AuthEventEmitter {
  private listeners = new Map<AuthEvent, Set<Listener>>();

  on(event: AuthEvent, callback: Listener) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);

    return () => this.off(event, callback);
  }

  off(event: AuthEvent, callback: Listener) {
    this.listeners.get(event)?.delete(callback);
  }

  emit(event: AuthEvent) {
    this.listeners.get(event)?.forEach(cb => {
      try { cb(event); } catch (err) { console.error(err); }
    });
  }
}

export const authEvents = new AuthEventEmitter();