#
# Base class for electrode submodels
#
import pybamm


class BaseElectrode(pybamm.BaseSubModel):
    """Base class for electrode submodels.

    Parameters
    ----------
    param : parameter class
        The parameters to use for this submodel
    domain : str
        Either 'Negative' or 'Positive'

    **Extends:** :class:`pybamm.BaseSubModel`
    """

    def __init__(self, param, domain):
        super().__init__(param)
        self._domain = domain

    def _get_standard_potential_variables(self, phi_s):
        """
        A private function to obtain the standard variables which
        can be derived from the potential in the electrode.

        Parameters
        ----------
        phi_s : :class:`pybamm.Symbol`
            The potential in the electrode.

        Returns
        -------
        variables : dict
            The variables which can be derived from the potential in the
            electrode.
        """
        param = self.param
        phi_s_av = pybamm.average(phi_s)

        if self._domain == "Negative":
            phi_s_dim = param.potential_scale * phi_s
            phi_s_av_dim = param.potential_scale * phi_s_av
            delta_phi_s = phi_s

        elif self._domain == "Positive":
            phi_s_dim = param.U_p_ref - param.U_n_ref + param.potential_scale * phi_s
            phi_s_av_dim = (
                param.U_p_ref - param.U_n_ref + param.potential_scale * phi_s_av
            )
            V = pybamm.BoundaryValue(phi_s, "right")
            delta_phi_s = phi_s - V

        delta_phi_s_av = pybamm.average(delta_phi_s)
        delta_phi_s_dim = delta_phi_s * param.potential_scale
        delta_phi_s_av_dim = delta_phi_s_av * param.potential_scale

        variables = {
            self._domain + " electrode potential": phi_s,
            self._domain + " electrode potential [V]": phi_s_dim,
            "Average " + self._domain.lower() + " electrode potential": phi_s_av,
            "Average "
            + self._domain.lower()
            + " electrode potential [V]": phi_s_av_dim,
            self._domain + " electrode ohmic losses": delta_phi_s,
            self._domain + " electrode ohmic losses [V]": delta_phi_s_dim,
            "Average "
            + self._domain.lower()
            + " electrode ohmic losses": delta_phi_s_av,
            "Average "
            + self._domain.lower()
            + " electrode ohmic losses [V]": delta_phi_s_av_dim,
        }

        return variables

    def _get_standard_current_variables(self, i_s):
        """
        A private function to obtain the standard variables which
        can be derived from the current in the electrode.

        Parameters
        ----------
        i_s : :class:`pybamm.Symbol`
            The current in the electrode.

        Returns
        -------
        variables : dict
            The variables which can be derived from the current in the
            electrode.
        """
        param = self.param

        i_s_dim = param.i_typ * i_s

        variables = {
            self._domain + " electrode current density": i_s,
            self._domain + " electrode current density [A.m-2]": i_s_dim,
        }

        return variables

    def _get_standard_whole_cell_current_variables(self, variables):
        """
        A private function to obtain the whole-cell versions of the
        current variables.

        Parameters
        ----------
        variables : dict
            The variables in the whole model.

        Returns
        -------
        variables : dict
            The variables in the whole model with the whole-cell
            current variables added.
        """
        i_s_n = variables["Negative electrode current density"]
        i_s_s = pybamm.Broadcast(0, ["separator"])
        i_s_p = variables["Positive electrode current density"]

        i_s = pybamm.Concatenation(i_s_n, i_s_s, i_s_p)

        variables.update({"Electrode current density": i_s})

        return variables

    @property
    def _domain(self):
        return self.__domain

    @_domain.setter
    def _domain(self, domain):
        if domain in ["Negative", "Positive"]:
            self.__domain = domain
        else:
            raise pybamm.DomainError(
                "Domain must be either 'Negative' or 'Positive' not {}".format(domain)
            )

    @property
    def default_solver(self):
        """
        Create and return the default solver for this model
        """
        return pybamm.ScikitsDaeSolver()