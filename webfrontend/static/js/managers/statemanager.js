// statemanager.js (Observer Pattern)
class StateManager {
    constructor() {
        this.state = {
            currentState: 'inspector_state',
            data: null
        };
        this.subscribers = [];
    }

    async transitionState(payload, endpoint='') {
        endpoint = endpoint || `/states/${this.state.currentState}`;
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            
            this.state = {
                currentState: result.nextState || this.state.currentState,
                actions: result.actions,
                data: result.data
            };
            console.log(this.state.currentState);

            this.notifySubscribers();

            return true;
        } catch (error) {
            console.error('State transition failed:', error)
            return false;
        }
    }

    subscribe(callback) {
        this.subscribers.push(callback);
        return () => this.unsubscribe(callback);
    }

    unsubscribe(callback) {
        this.subscribers = this.subscribers.filter(sub => sub !== callback);
    }

    notifySubscribers() {
        this.subscribers.forEach(callback => callback(this.state))
    }
}

export const statemanager = new StateManager();