/// <reference types="cypress" />

describe('Chain Builder', () => {
  beforeEach(() => {
    cy.visit('/chain-builder');
  });

  it('should load the chain builder page', () => {
    cy.get('[data-testid="react-flow"]').should('exist');
    cy.get('[data-testid="mcp-library"]').should('exist');
    cy.get('[data-testid="properties-panel"]').should('exist');
  });

  it('should add an MCP node to the canvas', () => {
    // Find and click the first MCP in the library
    cy.get('[data-testid="mcp-library"]')
      .find('[data-testid="mcp-card"]')
      .first()
      .click();

    // Verify the node was added to the canvas
    cy.get('[data-testid="react-flow"]')
      .find('[data-testid="node"]')
      .should('have.length', 1);
  });

  it('should connect nodes', () => {
    // Add two nodes
    cy.get('[data-testid="mcp-library"]')
      .find('[data-testid="mcp-card"]')
      .first()
      .click();
    cy.get('[data-testid="mcp-library"]')
      .find('[data-testid="mcp-card"]')
      .eq(1)
      .click();

    // Connect the nodes
    cy.get('[data-testid="node"]')
      .first()
      .trigger('mousedown', { button: 0 })
      .trigger('mousemove', { clientX: 200, clientY: 200 })
      .trigger('mouseup');

    // Verify the connection was created
    cy.get('[data-testid="edge"]').should('exist');
  });

  it('should update node properties', () => {
    // Add a node
    cy.get('[data-testid="mcp-library"]')
      .find('[data-testid="mcp-card"]')
      .first()
      .click();

    // Select the node
    cy.get('[data-testid="node"]').first().click();

    // Update properties
    cy.get('[data-testid="properties-panel"]')
      .find('input[name="model"]')
      .type('gpt-3.5-turbo');

    // Verify the update
    cy.get('[data-testid="node"]')
      .first()
      .should('contain', 'gpt-3.5-turbo');
  });

  it('should save and execute a chain', () => {
    // Add a node
    cy.get('[data-testid="mcp-library"]')
      .find('[data-testid="mcp-card"]')
      .first()
      .click();

    // Save the chain
    cy.get('[data-testid="save-button"]').click();
    cy.get('[data-testid="save-dialog"]')
      .find('input[name="name"]')
      .type('Test Chain');
    cy.get('[data-testid="save-dialog"]')
      .find('button[type="submit"]')
      .click();

    // Execute the chain
    cy.get('[data-testid="execute-button"]').click();

    // Verify execution started
    cy.get('[data-testid="execution-status"]')
      .should('contain', 'Running');
  });

  it('should handle errors gracefully', () => {
    // Add an invalid node configuration
    cy.get('[data-testid="mcp-library"]')
      .find('[data-testid="mcp-card"]')
      .first()
      .click();

    cy.get('[data-testid="node"]').first().click();
    cy.get('[data-testid="properties-panel"]')
      .find('input[name="temperature"]')
      .type('2'); // Invalid temperature value

    // Verify error message
    cy.get('[data-testid="error-message"]')
      .should('contain', 'Temperature must be between 0 and 1');
  });
}); 