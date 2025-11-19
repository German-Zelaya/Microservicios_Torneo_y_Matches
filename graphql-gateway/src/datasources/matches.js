const axios = require('axios');
const config = require('../config');

class MatchesAPI {
  constructor() {
    this.baseURL = `${config.services.matches}/api/v1/matches`;
  }

  async getMatches({ tournament_id, status, round }) {
    try {
      const params = {};
      if (tournament_id) params.tournament_id = tournament_id;
      if (status) params.status = status;
      if (round) params.round = round;

      const response = await axios.get(this.baseURL, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getMatch(id) {
    try {
      const response = await axios.get(`${this.baseURL}/${id}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createMatch(input) {
    try {
      const response = await axios.post(this.baseURL, input);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateMatch(id, input) {
    try {
      const response = await axios.put(`${this.baseURL}/${id}`, input);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteMatch(id) {
    try {
      await axios.delete(`${this.baseURL}/${id}`);
      return true;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async startMatch(id) {
    try {
      const response = await axios.patch(`${this.baseURL}/${id}/start`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async completeMatch(id) {
    try {
      const response = await axios.patch(`${this.baseURL}/${id}/complete`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async cancelMatch(id) {
    try {
      const response = await axios.patch(`${this.baseURL}/${id}/cancel`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async reportResult(id, input) {
    try {
      const response = await axios.post(`${this.baseURL}/${id}/result`, input);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async validateResult(id) {
    try {
      const response = await axios.put(`${this.baseURL}/${id}/validate`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async healthCheck() {
    try {
      const response = await axios.get(`${config.services.matches}/health`);
      return response.data;
    } catch (error) {
      throw new Error('Matches service is unavailable');
    }
  }

  handleError(error) {
    if (error.response) {
      const message = error.response.data?.message || error.response.data?.error || error.message;
      return new Error(`Matches Service Error: ${message}`);
    }
    return new Error(`Matches Service Error: ${error.message}`);
  }
}

module.exports = new MatchesAPI();
