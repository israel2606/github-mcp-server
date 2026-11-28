package transport

import (
	"context"
	"net/http"
	"testing"

	ghcontext "github.com/github/github-mcp-server/pkg/context"
	"github.com/github/github-mcp-server/pkg/http/headers"
	"github.com/stretchr/testify/require"
)

// capturingRoundTripper records the request it received and returns a canned
// 200 response, so tests can assert on the headers each transport sets without
// any network I/O.
type capturingRoundTripper struct {
	got *http.Request
}

func (c *capturingRoundTripper) RoundTrip(req *http.Request) (*http.Response, error) {
	c.got = req
	return &http.Response{StatusCode: http.StatusOK, Body: http.NoBody, Header: make(http.Header)}, nil
}

func newRequest(ctx context.Context, t *testing.T) *http.Request {
	t.Helper()
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, "https://api.github.com/", nil)
	require.NoError(t, err)
	return req
}

func TestUserAgentTransport_SetsHeaderAndPreservesOriginal(t *testing.T) {
	capture := &capturingRoundTripper{}
	tr := &UserAgentTransport{Transport: capture, Agent: "github-mcp-server/test"}

	req := newRequest(context.Background(), t)
	resp, err := tr.RoundTrip(req)
	require.NoError(t, err)
	defer func() { _ = resp.Body.Close() }()
	require.Equal(t, http.StatusOK, resp.StatusCode)

	// The outgoing (cloned) request carries the agent...
	require.Equal(t, "github-mcp-server/test", capture.got.Header.Get(headers.UserAgentHeader))
	// ...while the caller's original request is left untouched (Clone semantics).
	require.Empty(t, req.Header.Get(headers.UserAgentHeader))
}

func TestBearerAuthTransport_SetsAuthorization(t *testing.T) {
	capture := &capturingRoundTripper{}
	tr := &BearerAuthTransport{Transport: capture, Token: "secret-token"}

	resp, err := tr.RoundTrip(newRequest(context.Background(), t))
	require.NoError(t, err)
	defer func() { _ = resp.Body.Close() }()
	require.Equal(t, "Bearer secret-token", capture.got.Header.Get(headers.AuthorizationHeader))
	// No GraphQL features in context -> header must be absent.
	require.Empty(t, capture.got.Header.Get(headers.GraphQLFeaturesHeader))
}

func TestBearerAuthTransport_AddsGraphQLFeaturesFromContext(t *testing.T) {
	capture := &capturingRoundTripper{}
	tr := &BearerAuthTransport{Transport: capture, Token: "tok"}

	ctx := ghcontext.WithGraphQLFeatures(context.Background(), "feature_a", "feature_b")
	resp, err := tr.RoundTrip(newRequest(ctx, t))
	require.NoError(t, err)
	defer func() { _ = resp.Body.Close() }()
	require.Equal(t, "Bearer tok", capture.got.Header.Get(headers.AuthorizationHeader))
	require.Equal(t, "feature_a, feature_b", capture.got.Header.Get(headers.GraphQLFeaturesHeader))
}
