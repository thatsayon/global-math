export interface loginRequest {
    email: string;
    password: string;
}

export interface loginResponse {
    access: string;
    refresh: string;
    detail?: string;
}
