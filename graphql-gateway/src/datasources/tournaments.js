const axios = require('axios');
const config = require('../config');

class TournamentsAPI {
  constructor() {
    this.baseURL = `${config.services.tournaments}/api/v1/tournaments`;
  }

  async getTournaments({ page = 1, page_size = 10, game, status }) {
    try {
      const params = { page, page_size };
      if (game) params.game = game;
      if (status) params.status = status;

      const response = await axios.get(this.baseURL, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getTournament(id) {
    try {
      const response = await axios.get(`${this.baseURL}/${id}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createTournament(input) {
    try {
      const response = await axios.post(this.baseURL, input);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateTournament(id, input) {
    try {
      const response = await axios.put(`${this.baseURL}/${id}`, input);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteTournament(id) {
    try {
      await axios.delete(`${this.baseURL}/${id}`);
      return true;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async changeTournamentStatus(id, status) {
    try {
      const response = await axios.patch(`${this.baseURL}/${id}/status`, null, {
        params: { new_status: status }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async startTournament(id, input) {
    try {
      const response = await axios.post(`${this.baseURL}/${id}/start`, input);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async healthCheck() {
    try {
      const response = await axios.get(`${config.services.tournaments}/health`);
      return response.data;
    } catch (error) {
      throw new Error('Tournaments service is unavailable');
    }
  }

  handleError(error) {
    if (error.response) {
      const message = error.response.data?.detail || error.response.data?.message || error.message;
      return new Error(`Tournaments Service Error: ${message}`);
    }
    return new Error(`Tournaments Service Error: ${error.message}`);
  }
}

module.exports = new TournamentsAPI();
