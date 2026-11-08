package mark

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestWith_NilError(t *testing.T) {
	require.NoError(t, With(nil, ErrNotFound))
}

func TestWith_IsMatchesBothMarkAndWrapped(t *testing.T) {
	base := errors.New("row 42 missing")
	wrapped := With(base, ErrNotFound)

	// Matches the mark...
	require.ErrorIs(t, wrapped, ErrNotFound)
	// ...and still matches the underlying error (via Unwrap).
	require.ErrorIs(t, wrapped, base)
	// ...but not an unrelated mark.
	require.NotErrorIs(t, wrapped, ErrForbidden)
}

func TestWith_ErrorStringIncludesBoth(t *testing.T) {
	wrapped := With(errors.New("boom"), ErrBadRequest)
	require.Equal(t, "bad request: boom", wrapped.Error())
}

// customErr is a typed error so we can exercise the As path of the marked type.
type customErr struct{ msg string }

func (e customErr) Error() string { return e.msg }

func TestWith_AsMatchesMarkType(t *testing.T) {
	wrapped := With(errors.New("underlying"), customErr{msg: "marked"})

	var target customErr
	require.True(t, errors.As(wrapped, &target))
	require.Equal(t, "marked", target.msg)
}

func TestWith_Unwrap(t *testing.T) {
	base := errors.New("inner")
	require.Equal(t, base, errors.Unwrap(With(base, ErrTimedout)))
}
